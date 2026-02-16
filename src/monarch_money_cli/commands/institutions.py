"""
Institution management commands.
"""

import typer
from rich.table import Table

from monarch_money_cli.client import async_command, console, get_client, handle_error, output_json

app = typer.Typer(no_args_is_help=True)


@app.command("list")
@async_command
async def list_institutions(
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, table"),
):
    """
    List linked financial institutions.
    """
    try:
        mm = get_client()
        data = await mm.get_institutions()
        
        if format == "table":
            institutions = data.get("credentials", [])
            table = Table(title="Linked Institutions")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("Last Update")
            
            for i in institutions:
                inst = i.get("institution", {})
                status = i.get("updateRequired", False)
                status_str = "[red]Update Required[/red]" if status else "[green]OK[/green]"
                
                table.add_row(
                    i.get("id", ""),
                    inst.get("name", "Unknown"),
                    status_str,
                    i.get("lastUpdatedAt", ""),
                )
            console.print(table)
        else:
            output_json(data)
    except Exception as e:
        handle_error(e)


@app.command("subscription")
@async_command
async def get_subscription():
    """
    Get Monarch Money subscription details.
    """
    try:
        mm = get_client()
        data = await mm.get_subscription_details()
        output_json(data)
    except Exception as e:
        handle_error(e)
