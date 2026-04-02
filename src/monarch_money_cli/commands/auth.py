"""
Authentication commands.
"""

import typer
from rich.prompt import Prompt

from monarchmoney import MonarchMoney, RequireMFAException

from monarch_money_cli.client import (
    SESSION_FILE,
    async_command,
    clear_session,
    console,
    handle_error,
    save_session,
    session_exists,
)

app = typer.Typer(no_args_is_help=True)


@app.command("login")
@async_command
async def login():
    """
    Login to Monarch Money (interactive, supports MFA + trusted device).
    """
    try:
        mm = MonarchMoney()

        email = Prompt.ask("[bold]Email[/bold]")
        password = Prompt.ask("[bold]Password[/bold]", password=True)

        try:
            await mm.login(
                email=email,
                password=password,
                save_session=False,
                use_saved_session=False,
            )
        except RequireMFAException:
            console.print("[yellow]MFA required.[/yellow]")
            mfa_code = Prompt.ask("[bold]MFA Code[/bold]")
            await mm.multi_factor_authenticate(email, password, mfa_code)

        save_session(mm)

        console.print("[green]Login successful. Session saved.[/green]")
    except Exception as e:
        handle_error(e)


@app.command("logout")
def logout():
    """
    Clear saved session and logout.
    """
    if clear_session():
        console.print("[green]Session cleared.[/green]")
    else:
        console.print("[yellow]No active session found.[/yellow]")


@app.command("status")
def status():
    """
    Check authentication status.
    """
    if session_exists():
        console.print("[green]Authenticated[/green]")
        console.print(f"  Session file: {SESSION_FILE}")
    else:
        console.print("[red]Not authenticated[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
