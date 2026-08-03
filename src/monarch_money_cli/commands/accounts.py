"""
Account management commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import async_command, console, get_client, output_json

app = typer.Typer(no_args_is_help=True)


@app.command("list")
@async_command
async def list_accounts(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List all accounts.
    """
    mm = get_client()
    data = await mm.get_accounts()

    if format == "table":
        accounts = data.get("accounts", [])
        table = Table(title="Accounts")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Subtype")
        table.add_column("Balance", justify="right")
        table.add_column("Institution")

        for acc in accounts:
            table.add_row(
                acc.get("id", ""),
                acc.get("displayName", ""),
                acc.get("type", {}).get("name", ""),
                acc.get("subtype", {}).get("name", "") if acc.get("subtype") else "",
                f"${acc.get('currentBalance', 0):,.2f}",
                acc.get("institution", {}).get("name", "") if acc.get("institution") else "Manual",
            )
        console.print(table)
    else:
        output_json(data)


@app.command("get")
@async_command
async def get_account(
    account_id: str = typer.Argument(..., help="Account ID"),
):
    """
    Get details for a specific account.
    """
    mm = get_client()
    data = await mm.get_accounts()

    # Find the specific account
    accounts = data.get("accounts", [])
    account = next((a for a in accounts if a.get("id") == account_id), None)

    if account:
        output_json(account)
    else:
        console.print(f"[red]Account not found: {account_id}[/red]")
        raise SystemExit(1)


@app.command("holdings")
@async_command
async def get_holdings(
    account_id: str = typer.Argument(..., help="Account ID"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    Get holdings for an investment account.
    """
    mm = get_client()
    data = await mm.get_account_holdings(account_id)

    if format == "table":
        holdings = data.get("holdings", [])
        table = Table(title="Holdings")
        table.add_column("Symbol")
        table.add_column("Name")
        table.add_column("Quantity", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Value", justify="right")

        for h in holdings:
            table.add_row(
                h.get("ticker", ""),
                h.get("name", "")[:30],
                f"{h.get('quantity', 0):.4f}",
                f"${h.get('price', 0):,.2f}",
                f"${h.get('value', 0):,.2f}",
            )
        console.print(table)
    else:
        output_json(data)


@app.command("history")
@async_command
async def get_history(
    account_id: str = typer.Argument(..., help="Account ID"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    Get balance history for an account.
    """
    mm = get_client()
    data = await mm.get_account_history(account_id)

    if format == "table":
        history = data.get("history", [])[-30:]  # Last 30 entries
        table = Table(title="Account History (last 30 days)")
        table.add_column("Date")
        table.add_column("Balance", justify="right")

        for h in history:
            table.add_row(
                h.get("date", ""),
                f"${h.get('signedBalance', 0):,.2f}",
            )
        console.print(table)
    else:
        output_json(data)


@app.command("refresh")
@async_command
async def refresh_accounts(
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for refresh to complete"),
):
    """
    Trigger account sync with financial institutions.
    """
    mm = get_client()

    if wait:
        console.print("[yellow]Refreshing accounts (this may take a minute)...[/yellow]")
        await mm.request_accounts_refresh_and_wait()
        console.print("[green]✓ Accounts refreshed.[/green]")
    else:
        await mm.request_accounts_refresh()
        console.print("[green]✓ Account refresh requested.[/green]")
        console.print("[dim]Use --wait to wait for completion, or check status with 'monarch accounts refresh-status'[/dim]")


@app.command("refresh-status")
@async_command
async def refresh_status():
    """
    Check if account refresh is complete.
    """
    mm = get_client()
    is_complete = await mm.is_accounts_refresh_complete()

    if is_complete:
        console.print("[green]✓ Account refresh complete.[/green]")
    else:
        console.print("[yellow]Account refresh in progress...[/yellow]")


@app.command("types")
@async_command
async def list_account_types():
    """
    List available account types and subtypes.
    """
    mm = get_client()
    data = await mm.get_account_type_options()
    output_json(data)


@app.command("create")
@async_command
async def create_account(
    name: str = typer.Option(..., "--name", "-n", help="Account name"),
    account_type: str = typer.Option(..., "--type", "-t", help="Account type"),
    subtype: str = typer.Option(None, "--subtype", "-s", help="Account subtype"),
    balance: float = typer.Option(0.0, "--balance", "-b", help="Initial balance"),
):
    """
    Create a manual account.
    """
    mm = get_client()
    data = await mm.create_manual_account(
        account_type=account_type,
        account_sub_type=subtype,
        account_name=name,
        account_balance=balance,
    )
    console.print("[green]✓ Account created.[/green]")
    output_json(data)


@app.command("update")
@async_command
async def update_account(
    account_id: str = typer.Argument(..., help="Account ID"),
    name: str = typer.Option(None, "--name", "-n", help="New account name"),
    balance: float = typer.Option(None, "--balance", "-b", help="Update balance"),
    hidden: bool = typer.Option(None, "--hidden/--visible", help="Hide or show account"),
):
    """
    Update an account's settings.
    """
    mm = get_client()

    kwargs = {"account_id": account_id}
    if name is not None:
        kwargs["account_name"] = name
    if balance is not None:
        kwargs["account_balance"] = balance
    if hidden is not None:
        kwargs["hide_from_list"] = hidden

    data = await mm.update_account(**kwargs)
    console.print("[green]✓ Account updated.[/green]")
    output_json(data)


@app.command("delete")
@async_command
async def delete_account(
    account_id: str = typer.Argument(..., help="Account ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    Delete an account.
    """
    if not confirm:
        confirm = typer.confirm("Are you sure you want to delete this account?")

    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        raise SystemExit(0)

    mm = get_client()
    await mm.delete_account(account_id)
    console.print("[green]✓ Account deleted.[/green]")
