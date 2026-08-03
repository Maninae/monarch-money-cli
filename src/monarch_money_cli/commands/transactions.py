"""
Transaction management commands.
"""

from datetime import datetime

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

# The API requires both ends of a date range; this start means "all history".
EARLIEST_TRANSACTION_START_DATE = "2000-01-01"


@app.command("list")
@async_command
async def list_transactions(
    limit: int = typer.Option(100, "--limit", "-l", help="Number of transactions to return"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset for pagination"),
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    search: str = typer.Option(None, "--search", "-q", help="Search query"),
    account_ids: str = typer.Option(None, "--accounts", "-a", help="Comma-separated account IDs"),
    category_ids: str = typer.Option(None, "--categories", "-c", help="Comma-separated category IDs"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List transactions with optional filters.
    """
    mm = get_client()

    kwargs = {"limit": limit, "offset": offset}

    if start_date and not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if end_date and not start_date:
        start_date = EARLIEST_TRANSACTION_START_DATE
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    if search:
        kwargs["search"] = search
    if account_ids:
        kwargs["account_ids"] = account_ids.split(",")
    if category_ids:
        kwargs["category_ids"] = category_ids.split(",")

    data = await mm.get_transactions(**kwargs)

    if format == "table":
        txns = data.get("allTransactions", {}).get("results", [])
        table = Table(title=f"Transactions (showing {len(txns)})")
        table.add_column("Date")
        table.add_column("Merchant")
        table.add_column("Category")
        table.add_column("Amount", justify="right")
        table.add_column("Account")

        for t in txns:
            amount = t.get("amount", 0)
            amount_str = f"${abs(amount):,.2f}"
            if amount < 0:
                amount_str = f"[red]-{amount_str}[/red]"
            else:
                amount_str = f"[green]+{amount_str}[/green]"

            table.add_row(
                t.get("date", ""),
                (t.get("merchant") or {}).get("name", t.get("plaidName", ""))[:25],
                (t.get("category") or {}).get("name", ""),
                amount_str,
                (t.get("account") or {}).get("displayName", "")[:15],
            )
        console.print(table)
    else:
        output_json(data)


@app.command("get")
@async_command
async def get_transaction(
    transaction_id: str = typer.Argument(..., help="Transaction ID"),
):
    """
    Get details for a specific transaction.
    """
    mm = get_client()
    data = await mm.get_transaction_details(transaction_id)
    output_json(data)


@app.command("summary")
@async_command
async def get_summary(
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
):
    """
    Get transaction summary for a date range.
    """
    mm = get_client()
    start_date, end_date = default_date_range(start_date, end_date)

    data = await mm.get_transactions_summary(start_date=start_date, end_date=end_date)
    output_json(data)


@app.command("create")
@async_command
async def create_transaction(
    date: str = typer.Option(..., "--date", "-d", help="Transaction date (YYYY-MM-DD)"),
    account_id: str = typer.Option(..., "--account", "-a", help="Account ID"),
    amount: float = typer.Option(..., "--amount", help="Transaction amount (negative for expense)"),
    merchant: str = typer.Option(None, "--merchant", "-m", help="Merchant name"),
    category_id: str = typer.Option(None, "--category", "-c", help="Category ID"),
    notes: str = typer.Option(None, "--notes", "-n", help="Transaction notes"),
):
    """
    Create a new transaction.
    """
    mm = get_client()
    data = await mm.create_transaction(
        date=date,
        account_id=account_id,
        amount=amount,
        merchant_name=merchant,
        category_id=category_id,
        notes=notes,
    )
    console.print("[green]✓ Transaction created.[/green]")
    output_json(data)


@app.command("update")
@async_command
async def update_transaction(
    transaction_id: str = typer.Argument(..., help="Transaction ID"),
    category_id: str = typer.Option(None, "--category", "-c", help="New category ID"),
    merchant: str = typer.Option(None, "--merchant", "-m", help="New merchant name"),
    notes: str = typer.Option(None, "--notes", "-n", help="New notes"),
    hide: bool = typer.Option(None, "--hide/--show", help="Hide or show transaction"),
):
    """
    Update an existing transaction.
    """
    mm = get_client()

    kwargs = {"transaction_id": transaction_id}
    if category_id is not None:
        kwargs["category_id"] = category_id
    if merchant is not None:
        kwargs["merchant_name"] = merchant
    if notes is not None:
        kwargs["notes"] = notes
    if hide is not None:
        kwargs["hide_from_reports"] = hide

    data = await mm.update_transaction(**kwargs)
    console.print("[green]✓ Transaction updated.[/green]")
    output_json(data)


@app.command("delete")
@async_command
async def delete_transaction(
    transaction_id: str = typer.Argument(..., help="Transaction ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    Delete a transaction.
    """
    if not confirm:
        confirm = typer.confirm("Are you sure you want to delete this transaction?")

    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        raise SystemExit(0)

    mm = get_client()
    await mm.delete_transaction(transaction_id)
    console.print("[green]✓ Transaction deleted.[/green]")


@app.command("splits")
@async_command
async def get_splits(
    transaction_id: str = typer.Argument(..., help="Transaction ID"),
):
    """
    Get splits for a transaction.
    """
    mm = get_client()
    data = await mm.get_transaction_splits(transaction_id)
    output_json(data)
