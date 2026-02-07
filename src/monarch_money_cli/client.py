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

console = Console()

# Default session path
SESSION_DIR = Path.home() / ".monarch"
SESSION_FILE = SESSION_DIR / "session.json"


def get_client(require_auth: bool = True) -> MonarchMoney:
    """Get a MonarchMoney client, optionally loading saved session."""
    mm = MonarchMoney()
    
    if require_auth and SESSION_FILE.exists():
        try:
            mm.load_session(str(SESSION_FILE))
        except Exception as e:
            if require_auth:
                console.print(f"[red]Failed to load session: {e}[/red]")
                console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
                raise SystemExit(1)
    elif require_auth:
        console.print("[red]Not authenticated.[/red]")
        console.print("[yellow]Run 'monarch auth login' to authenticate.[/yellow]")
        raise SystemExit(1)
    
    return mm


def save_session(mm: MonarchMoney) -> None:
    """Save the current session."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    mm.save_session(str(SESSION_FILE))


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


def handle_error(e: Exception) -> None:
    """Handle and display errors consistently."""
    console.print(f"[red]Error: {e}[/red]")
    raise SystemExit(1)
