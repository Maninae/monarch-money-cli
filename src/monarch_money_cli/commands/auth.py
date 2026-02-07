"""
Authentication commands.
"""

import typer
from rich.console import Console
from rich.prompt import Prompt

from monarchmoney import MonarchMoney, RequireMFAException

from monarch_money_cli.client import (
    SESSION_FILE,
    async_command,
    clear_session,
    save_session,
    session_exists,
)

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("login")
@async_command
async def login(
    email: str = typer.Option(None, "--email", "-e", help="Monarch Money email"),
    password: str = typer.Option(None, "--password", "-p", help="Monarch Money password"),
    mfa_secret: str = typer.Option(None, "--mfa-secret", help="MFA secret key for automatic TOTP"),
):
    """
    Login to Monarch Money (interactive, supports MFA).
    """
    mm = MonarchMoney()
    
    # Get credentials interactively if not provided
    if not email:
        email = Prompt.ask("[bold]Email[/bold]")
    if not password:
        password = Prompt.ask("[bold]Password[/bold]", password=True)
    
    try:
        if mfa_secret:
            # Use MFA secret for automatic TOTP generation
            await mm.login(
                email=email,
                password=password,
                save_session=False,
                use_saved_session=False,
                mfa_secret_key=mfa_secret,
            )
        else:
            # Try login, may require MFA
            await mm.login(email, password)
    except RequireMFAException:
        console.print("[yellow]MFA required.[/yellow]")
        mfa_code = Prompt.ask("[bold]MFA Code[/bold]")
        await mm.multi_factor_authenticate(email, password, mfa_code)
    
    # Save session for future use
    save_session(mm)
    console.print("[green]✓ Login successful. Session saved.[/green]")


@app.command("logout")
def logout():
    """
    Clear saved session and logout.
    """
    if clear_session():
        console.print("[green]✓ Session cleared.[/green]")
    else:
        console.print("[yellow]No active session found.[/yellow]")


@app.command("status")
def status():
    """
    Check authentication status.
    """
    if session_exists():
        console.print(f"[green]✓ Authenticated[/green]")
        console.print(f"  Session file: {SESSION_FILE}")
    else:
        console.print("[red]✗ Not authenticated[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
