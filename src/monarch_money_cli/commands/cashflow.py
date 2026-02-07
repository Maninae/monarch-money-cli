"""
Cashflow analysis commands.
"""

from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from monarch_money_cli.client import async_command, get_client, handle_error, output_json

app = typer.Typer(no_args_is_help=True)
console = Console()


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
    try:
        mm = get_client()
        
        # Default to current month
        if not start_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await mm.get_cashflow_summary(start_date=start_date, end_date=end_date)
        
        if format == "table":
            summary = data.get("summary", [{}])[0] if data.get("summary") else {}
            
            income = summary.get("sumIncome", 0)
            expenses = abs(summary.get("sumExpense", 0))
            savings = summary.get("savings", 0)
            savings_rate = summary.get("savingsRate", 0) * 100
            
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
    except Exception as e:
        handle_error(e)


@app.command("details")
@async_command
async def cashflow_details(
    start_date: str = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
):
    """
    Get detailed cashflow by category, category group, and merchant.
    """
    try:
        mm = get_client()
        
        # Default to current month
        if not start_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await mm.get_cashflow(start_date=start_date, end_date=end_date)
        output_json(data)
    except Exception as e:
        handle_error(e)
