"""
Tag management commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import async_command, console, get_client, output_json

app = typer.Typer(no_args_is_help=True)


@app.command("list")
@async_command
async def list_tags(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List all transaction tags.
    """
    mm = get_client()
    data = await mm.get_transaction_tags()

    if format == "table":
        tags = data.get("householdTransactionTags", [])
        table = Table(title="Tags")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Color")

        for t in tags:
            table.add_row(
                t.get("id", ""),
                t.get("name", ""),
                t.get("color", ""),
            )
        console.print(table)
    else:
        output_json(data)


@app.command("create")
@async_command
async def create_tag(
    name: str = typer.Argument(..., help="Tag name"),
    color: str = typer.Option(None, "--color", "-c", help="Tag color (hex)"),
):
    """
    Create a new transaction tag.
    """
    mm = get_client()
    data = await mm.create_transaction_tag(name=name, color=color)
    console.print("[green]✓ Tag created.[/green]")
    output_json(data)


@app.command("set")
@async_command
async def set_tags(
    transaction_id: str = typer.Argument(..., help="Transaction ID"),
    tag_ids: str = typer.Argument(..., help="Comma-separated tag IDs"),
):
    """
    Set tags on a transaction.
    """
    mm = get_client()
    tags = tag_ids.split(",")
    data = await mm.set_transaction_tags(transaction_id=transaction_id, tag_ids=tags)
    console.print("[green]✓ Tags set.[/green]")
    output_json(data)
