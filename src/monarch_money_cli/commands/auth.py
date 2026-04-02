"""
Authentication commands.
"""

import typer
from rich.prompt import Prompt

from monarchmoney import MonarchMoney, RequireMFAException

from monarch_money_cli.client import (
    SESSION_FILE,
    _load_config,
    async_command,
    clear_session,
    console,
    handle_error,
    save_config,
    save_session,
    session_exists,
)

app = typer.Typer(no_args_is_help=True)


def _get_device_uuid(config: dict, cli_uuid: str | None) -> str:
    """Get Device UUID from CLI arg, config, or interactive prompt."""
    if cli_uuid:
        return cli_uuid

    if config.get("device_uuid"):
        console.print("[dim]Using saved Device UUID.[/dim]")
        return config["device_uuid"]

    console.print()
    console.print("[bold]Device UUID required for long-lived tokens.[/bold]")
    console.print("To get it: log into app.monarchmoney.com in your browser,")
    console.print('  open DevTools Console, run: localStorage.getItem("monarchDeviceUUID")')
    console.print()
    uuid = Prompt.ask("[bold]Device UUID[/bold]")
    if not uuid.strip():
        console.print("[red]Device UUID is required.[/red]")
        raise SystemExit(1)
    return uuid.strip()


@app.command("login")
@async_command
async def login(
    email: str = typer.Option(None, "--email", "-e", help="Monarch Money email"),
    password: str = typer.Option(None, "--password", "-p", help="Monarch Money password"),
    mfa_secret: str = typer.Option(None, "--mfa-secret", help="MFA secret key for automatic TOTP"),
    device_uuid: str = typer.Option(None, "--device-uuid", help="Device UUID for long-lived tokens"),
):
    """
    Login to Monarch Money (interactive, supports MFA + trusted device).
    """
    try:
        config = _load_config()
        uuid = _get_device_uuid(config, device_uuid)

        mm = MonarchMoney()

        if not email:
            email = Prompt.ask("[bold]Email[/bold]")
        if not password:
            password = Prompt.ask("[bold]Password[/bold]", password=True)

        # Set Device-UUID header before login for long-lived tokens
        mm._headers["Device-UUID"] = uuid

        try:
            if mfa_secret:
                await mm.login(
                    email=email,
                    password=password,
                    save_session=False,
                    use_saved_session=False,
                    mfa_secret_key=mfa_secret,
                )
            else:
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

        # Persist Device UUID for future use
        config["device_uuid"] = uuid
        save_config(config)

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
        config = _load_config()
        if config.get("device_uuid"):
            console.print("  Device UUID: configured")
        else:
            console.print("  [yellow]Device UUID: not set (tokens may expire quickly)[/yellow]")
    else:
        console.print("[red]Not authenticated[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
