"""
Authentication commands.
"""

import typer
from monarchmoney import MonarchMoney, RequireMFAException
from rich.prompt import Prompt

from monarch_money_cli.client import (
    SESSION_FILE,
    async_command,
    clear_session,
    console,
    get_client,
    save_session,
    session_exists,
    verify_session,
)

app = typer.Typer(no_args_is_help=True)


@app.command("login")
@async_command
async def login():
    """
    Login to Monarch Money (interactive, supports MFA + trusted device).
    """
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
@async_command
async def status(
    verify: bool = typer.Option(False, "--verify", "-v", help="Also check the session against the API"),
):
    """
    Check authentication status. Exits 1 if not authenticated.

    Without --verify this only checks that a session file exists; the token
    may still have expired server-side.
    """
    if not session_exists():
        console.print("[red]Not authenticated[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
        raise SystemExit(1)

    console.print("[green]Authenticated[/green]")
    console.print(f"  Session file: {SESSION_FILE}")

    if verify:
        mm = get_client()
        await verify_session(mm)
        console.print("[green]  Session verified against the API.[/green]")
