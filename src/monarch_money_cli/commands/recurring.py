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
    List recurring transactions.
    """
    try:
        mm = get_client()
        data = await mm.get_recurring_transactions()
        
        if format == "table":
            recurring = data.get("recurringTransactions", [])
            table = Table(title="Recurring Transactions")
            table.add_column("Merchant")
            table.add_column("Amount", justify="right")
            table.add_column("Frequency")
            table.add_column("Next Date")
            table.add_column("Account")
            
            for r in recurring:
                amount = r.get("amount", 0)
                amount_str = f"${abs(amount):,.2f}"
                if amount < 0:
                    amount_str = f"[red]{amount_str}[/red]"
                else:
                    amount_str = f"[green]{amount_str}[/green]"
                
                table.add_row(
                    (r.get("merchant", {}) or {}).get("name", "Unknown")[:25],
                    amount_str,
                    r.get("frequency", ""),
                    r.get("nextExpectedDate", ""),
                    (r.get("account", {}) or {}).get("displayName", "")[:15],
                )
            console.print(table)
        else:
            output_json(data)
    except Exception as e:
        handle_error(e)
