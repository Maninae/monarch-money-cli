"""
Budget management commands.
"""

from datetime import datetime

import typer
from rich.table import Table

from monarch_money_cli.client import (
    async_command,
    console,
    get_client,
    output_json,
)

app = typer.Typer(no_args_is_help=True)


def budget_month_range(start: str | None, end: str | None) -> tuple[str, str]:
    """Budget-specific date range: defaults to full current month."""
    today = datetime.now()
    if not start:
        start = today.replace(day=1).strftime("%Y-%m-%d")
    if not end:
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1).strftime("%Y-%m-%d")
        else:
            end = today.replace(month=today.month + 1, day=1).strftime("%Y-%m-%d")
    return start, end


@app.command("list")
@async_command
async def list_budgets(
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List all budgets with actual amounts.
    """
    mm = get_client()
    start_date, end_date = budget_month_range(start_date, end_date)

    data = await mm.get_budgets(start_date=start_date, end_date=end_date)

    if format == "table":
        categories = data.get("budgetData", {}).get("monthlyAmountsByCategory", [])
        table = Table(title=f"Budgets ({start_date} to {end_date})")
        table.add_column("Category")
        table.add_column("Budgeted", justify="right")
        table.add_column("Actual", justify="right")
        table.add_column("Remaining", justify="right")
        table.add_column("Progress")

        for entry in categories:
            cat_name = (entry.get("category") or {}).get("name", "Unknown")
            amounts = entry.get("monthlyAmounts", [{}])
            budgeted = sum(a.get("plannedCashFlowAmount") or 0 for a in amounts)
            actual = sum(abs(a.get("actualAmount") or 0) for a in amounts)
            remaining = budgeted - actual

            if budgeted <= 0:
                continue

            pct = (actual / budgeted) * 100
            if pct > 100:
                progress = f"[red]{pct:.0f}%[/red]"
            elif pct > 80:
                progress = f"[yellow]{pct:.0f}%[/yellow]"
            else:
                progress = f"[green]{pct:.0f}%[/green]"

            remaining_str = (
                f"${remaining:,.2f}" if remaining >= 0
                else f"[red]-${abs(remaining):,.2f}[/red]"
            )

            table.add_row(
                cat_name,
                f"${budgeted:,.2f}",
                f"${actual:,.2f}",
                remaining_str,
                progress,
            )
        console.print(table)
    else:
        output_json(data)


@app.command("set")
@async_command
async def set_budget(
    category_id: str = typer.Argument(..., help="Category ID"),
    amount: float = typer.Argument(..., help="Budget amount (0 to clear)"),
    date: str = typer.Option(None, "--date", "-d", help="Month to set (YYYY-MM-DD, defaults to current)"),
    apply_to_future: bool = typer.Option(False, "--future", "-f", help="Apply to future months too"),
):
    """
    Set a budget amount for a category.

    Use amount=0 to clear/unset the budget.
    """
    mm = get_client()

    if not date:
        date = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    data = await mm.set_budget_amount(
        category_id=category_id,
        amount=amount,
        start_date=date,
        apply_to_future=apply_to_future,
    )

    if amount == 0:
        console.print("[green]Budget cleared.[/green]")
    else:
        console.print(f"[green]Budget set to ${amount:,.2f}.[/green]")
    output_json(data)
