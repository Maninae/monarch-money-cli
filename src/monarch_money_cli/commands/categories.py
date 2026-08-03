"""
Category management commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import async_command, console, get_client, output_json

app = typer.Typer(no_args_is_help=True)


@app.command("list")
@async_command
async def list_categories(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List all transaction categories.
    """
    mm = get_client()
    data = await mm.get_transaction_categories()

    if format == "table":
        categories = data.get("categories", [])
        table = Table(title="Categories")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Group")
        table.add_column("Icon")

        for c in categories:
            table.add_row(
                c.get("id", ""),
                c.get("name", ""),
                c.get("group", {}).get("name", "") if c.get("group") else "",
                c.get("icon", ""),
            )
        console.print(table)
    else:
        output_json(data)


@app.command("groups")
@async_command
async def list_category_groups(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List all category groups.
    """
    mm = get_client()
    data = await mm.get_transaction_category_groups()

    if format == "table":
        groups = data.get("categoryGroups", [])
        table = Table(title="Category Groups")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")

        for g in groups:
            table.add_row(
                g.get("id", ""),
                g.get("name", ""),
                g.get("type", ""),
            )
        console.print(table)
    else:
        output_json(data)


@app.command("create")
@async_command
async def create_category(
    name: str = typer.Argument(..., help="Category name"),
    group_id: str = typer.Option(None, "--group", "-g", help="Category group ID"),
    icon: str = typer.Option(None, "--icon", "-i", help="Icon name"),
):
    """
    Create a new transaction category.
    """
    mm = get_client()
    data = await mm.create_transaction_category(
        name=name,
        group_id=group_id,
        icon=icon,
    )
    console.print("[green]✓ Category created.[/green]")
    output_json(data)


@app.command("delete")
@async_command
async def delete_category(
    category_id: str = typer.Argument(..., help="Category ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    Delete a category.
    """
    if not confirm:
        confirm = typer.confirm("Are you sure you want to delete this category?")

    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        raise SystemExit(0)

    mm = get_client()
    await mm.delete_transaction_category(category_id)
    console.print("[green]✓ Category deleted.[/green]")
