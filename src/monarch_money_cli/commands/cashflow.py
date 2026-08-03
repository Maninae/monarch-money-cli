"""
Cashflow analysis commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import (
    async_command,
    console,
    default_date_range,
    get_client,
    output_json,
)

app = typer.Typer(no_args_is_help=True)


@app.command("summary")
@async_command
async def cashflow_summary(
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    Get cashflow summary (income, expenses, savings, savings rate).
    """
    mm = get_client()
    start_date, end_date = default_date_range(start_date, end_date)

    data = await mm.get_cashflow_summary(start_date=start_date, end_date=end_date)

    if format == "table":
        # API returns nested structure: {"summary": [{"summary": {...}}]}
        outer = data.get("summary", [{}])[0] if data.get("summary") else {}
        summary = outer.get("summary", {}) if isinstance(outer, dict) else {}

        income = summary.get("sumIncome", 0)
        expenses = abs(summary.get("sumExpense", 0))
        savings = income - expenses
        savings_rate = (savings / income * 100) if income else 0

        table = Table(title=f"Cashflow Summary ({start_date} to {end_date})")
        table.add_column("Metric")
        table.add_column("Amount", justify="right")

        table.add_row("Income", f"[green]${income:,.2f}[/green]")
        table.add_row("Expenses", f"[red]${expenses:,.2f}[/red]")
        table.add_row("Net Savings", f"${savings:,.2f}")
        table.add_row("Savings Rate", f"{savings_rate:.1f}%")

        console.print(table)
    else:
        output_json(data)


@app.command("details")
@async_command
async def cashflow_details(
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
):
    """
    Get detailed cashflow by category, category group, and merchant.
    """
    mm = get_client()
    start_date, end_date = default_date_range(start_date, end_date)

    data = await mm.get_cashflow(start_date=start_date, end_date=end_date)
    output_json(data)
