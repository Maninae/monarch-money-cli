"""
Monarch Money client singleton and session management.
"""

import asyncio
import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from monarchmoney import MonarchMoney
from rich.console import Console

# trusted_device must be True for non-expiring tokens
# See: https://github.com/hammem/monarchmoney/issues/139
import monarchmoney.monarchmoney as _mm_module


async def _login_user_patched(self, email, password, mfa_secret_key=None):
    """Login with trusted_device=True for non-expiring tokens."""
    from aiohttp import ClientSession

    data = {
        "password": password,
        "supports_mfa": True,
        "trusted_device": True,
        "username": email,
    }
    if mfa_secret_key:
        import oathtool
        data["totp"] = oathtool.generate_otp(mfa_secret_key)

    async with ClientSession(headers=self._headers) as session:
        async with session.post(
            _mm_module.MonarchMoneyEndpoints.getLoginEndpoint(), json=data
        ) as resp:
            if resp.status == 403:
                from monarchmoney import RequireMFAException
                raise RequireMFAException("Multi-Factor Auth Required")
            elif resp.status != 200:
                raise _mm_module.LoginFailedException(
                    f"HTTP Code {resp.status}: {resp.reason}"
                )
            response = await resp.json()
            self.set_token(response["token"])
            self._headers["Authorization"] = f"Token {self._token}"


_mm_module.MonarchMoney._login_user = _login_user_patched
del _mm_module

console = Console()

# Default session/config paths
SESSION_DIR = Path.home() / ".monarch"
SESSION_FILE = SESSION_DIR / "session.json"
CONFIG_FILE = SESSION_DIR / "config.json"


def _load_config() -> dict:
    """Load config from ~/.monarch/config.json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return {}


def save_config(config: dict) -> None:
    """Save config to ~/.monarch/config.json."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_client(require_auth: bool = True) -> MonarchMoney:
    """Get a MonarchMoney client, optionally loading saved session."""
    mm = MonarchMoney()

    if require_auth and SESSION_FILE.exists():
        try:
            mm.load_session(str(SESSION_FILE))
        except Exception:
            console.print("[red]Failed to load session.[/red]")
            console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
            raise SystemExit(1)
    elif require_auth:
        console.print("[red]Not authenticated.[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
        raise SystemExit(1)

    # Restore Device-UUID header for long-lived tokens
    config = _load_config()
    device_uuid = config.get("device_uuid")
    if device_uuid:
        mm._headers["Device-UUID"] = device_uuid

    return mm


async def verify_session(mm: MonarchMoney) -> None:
    """Health check: verify session is still valid. Call from async context."""
    try:
        await mm.get_subscription_details()
    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err or "not authenticated" in err.lower():
            console.print("[red]Session expired or invalid.[/red]")
            console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
            raise SystemExit(1)
        raise


def save_session(mm: MonarchMoney) -> None:
    """Save the current session."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_DIR.chmod(0o700)
    mm.save_session(str(SESSION_FILE))
    SESSION_FILE.chmod(0o600)


def clear_session() -> bool:
    """Clear saved session. Returns True if session existed."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        return True
    return False


def session_exists() -> bool:
    """Check if a session file exists."""
    return SESSION_FILE.exists()


def async_command(f: Callable) -> Callable:
    """Decorator to run async functions in typer commands."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


def output_json(data: Any) -> None:
    """Output data as JSON."""
    console.print_json(json.dumps(data, default=str, indent=2))


def _friendly_message(e: Exception) -> str:
    """Convert upstream exceptions into user-friendly messages."""
    from monarchmoney.monarchmoney import LoginFailedException, RequestFailedException

    msg = str(e)

    if isinstance(e, LoginFailedException):
        if "403" in msg:
            return "Login failed -- incorrect email, password, or MFA code."
        if "404" in msg:
            return "Login failed -- email address not found."
        if "401" in msg:
            return "Login failed -- incorrect password."
        if "525" in msg:
            return "Login failed -- could not connect to Monarch Money (SSL error). Try again later."
        return f"Login failed -- {_sanitize(msg)}"

    if isinstance(e, RequestFailedException):
        return f"API request failed -- {_sanitize(msg)}"

    if "TransportQueryError" in type(e).__name__:
        return "The Monarch Money API returned an error. The query may be temporarily unsupported."

    if isinstance(e, (ConnectionError, OSError)):
        return "Could not connect to Monarch Money. Check your internet connection."

    if isinstance(e, TimeoutError):
        return "Request to Monarch Money timed out. Try again."

    return _sanitize(msg)


def _sanitize(msg: str) -> str:
    """Strip tokens, headers, and URLs with auth params from error messages."""
    if any(kw in msg.lower() for kw in ("token", "bearer", "authorization", "set-cookie", "cf-ray", "clientresponse")):
        return "An authentication error occurred. Try logging in again with 'monarch auth login'."
    if len(msg) > 200:
        return msg[:200] + "..."
    return msg


def handle_error(e: Exception) -> None:
    """Handle and display errors consistently.

    Re-raises KeyboardInterrupt and SystemExit to allow clean exits.
    """
    if isinstance(e, (KeyboardInterrupt, SystemExit)):
        raise e
    console.print(f"[red]Error: {_friendly_message(e)}[/red]")
    raise SystemExit(1)


def default_date_range(start: str | None, end: str | None) -> tuple[str, str]:
    """Return (start_date, end_date), defaulting to current month."""
    from datetime import datetime
    today = datetime.now()
    return (
        start or today.replace(day=1).strftime("%Y-%m-%d"),
        end or today.strftime("%Y-%m-%d"),
    )


def print_table(
    title: str,
    columns: list[tuple[str, str]],
    rows: list[list[str]],
) -> None:
    """Print a simple table."""
    from rich.table import Table
    table = Table(title=title)
    for name, justify in columns:
        table.add_column(name, justify=justify or "left")
    for row in rows:
        table.add_row(*row)
    console.print(table)
