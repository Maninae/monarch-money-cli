"""
Recurring transactions commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import async_command, console, get_client, handle_error, output_json

app = typer.Typer(no_args_is_help=True)


@app.command("list")
@async_command
async def list_recurring(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List recurring transactions with estimated monthly totals.
    """
    try:
        mm = get_client()
        data = await mm.get_recurring_transactions()

        if format == "table":
            items = data.get("recurringTransactionItems", [])

            if not items:
                console.print("[yellow]No recurring transactions found[/yellow]")
                return

            table = Table(title=f"Recurring Transactions ({len(items)} items)")
            table.add_column("Merchant", max_width=30)
            table.add_column("Category")
            table.add_column("Amount", justify="right")
            table.add_column("Frequency")
            table.add_column("Date")
            table.add_column("Account", max_width=20)

            monthly_total = 0

            for item in items:
                stream = item.get("stream", {}) or {}
                merchant = stream.get("merchant", {}) or {}
                # Category and account are at the item level, not stream level
                category = item.get("category", {}) or {}
                account = item.get("account", {}) or {}

                merchant_name = merchant.get("name", "Unknown")[:30]
                category_name = category.get("name", "-")
                amount = abs(stream.get("amount", 0))
                frequency = stream.get("frequency", "-")
                next_date = item.get("date", "-")
                account_name = account.get("displayName", "-")[:20]

                # Estimate monthly amount
                if frequency == "weekly":
                    monthly_total += amount * 4.33
                elif frequency == "biweekly":
                    monthly_total += amount * 2.17
                elif frequency == "monthly":
                    monthly_total += amount
                elif frequency == "quarterly":
                    monthly_total += amount / 3
                elif frequency in ("yearly", "annual"):
                    monthly_total += amount / 12

                table.add_row(
                    merchant_name,
                    category_name,
                    f"[red]${amount:,.2f}[/red]",
                    frequency,
                    next_date,
                    account_name,
                )
            console.print(table)
            console.print(f"\n[bold]Estimated Monthly Total: ${monthly_total:,.2f}[/bold]")
        else:
            output_json(data)
    except Exception as e:
        handle_error(e)
