<div align="center">

# Monarch Money CLI 🦋

Query your finances from the terminal. Accounts, transactions, budgets, cashflow — one command away.

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Non--Commercial-F5A623?style=for-the-badge" alt="License"></a>

</div>

---

- **Full API coverage** — accounts, transactions, budgets, cashflow, categories, tags, recurring, institutions
- **Agent-friendly** — JSON output by default, structured for scripts and AI agents
- **Human-friendly** — `--format table` for readable output, interactive auth with MFA
- **Long-lived sessions** — trusted device support for non-expiring tokens

## Quick Start

```bash
git clone https://github.com/Maninae/monarch-money-cli.git
cd monarch-money-cli
pip install -e .
```

```bash
monarch auth login                  # interactive — prompts for email, password, MFA
monarch accounts list               # JSON by default
monarch accounts list --format table # human-readable
monarch transactions list --limit 20
monarch cashflow summary
```

## Commands

| Group | Commands |
|-------|----------|
| **auth** | `login` `logout` `status` |
| **accounts** | `list` `get` `holdings` `history` `refresh` `refresh-status` `types` `create` `update` `delete` |
| **transactions** | `list` `get` `summary` `create` `update` `delete` `splits` |
| **budgets** | `list` `set` |
| **cashflow** | `summary` `details` |
| **categories** | `list` `groups` `create` `delete` |
| **tags** | `list` `create` `set` |
| **recurring** | `list` |
| **institutions** | `list` `subscription` |

Every command supports `--help` for full usage details.

`monarch auth status` exits nonzero when not authenticated, and `monarch auth status --verify` round-trips the session against the API — handy for scripts and cron jobs that need to know a token died before they hit it.

## Output Formats

```bash
monarch accounts list                 # JSON (default)
monarch accounts list --format table  # table
```

JSON output works well with `jq` for scripting:

```bash
monarch transactions list --limit 100 | jq '.allTransactions.results[].amount'
```

## Configuration

| File | Contents | Permissions |
|------|----------|-------------|
| `~/.monarch/session.json` | Auth token (plain JSON) | `600` |
| `~/.monarch/` | Session directory | `700` |

Legacy sessions written by older versions were pickles despite the `.json` name; they are converted to real JSON automatically on first load.

## Security

- **All credentials are entered interactively** — nothing leaks to shell history or process lists.
- **Session file** is created with restricted permissions (`600`). Treat `~/.monarch/` like any credential store.
- **Logging out** (`monarch auth logout`) clears the local session file but does not revoke the token server-side.

## Dependencies

Built on the [monarchmoney](https://github.com/hammem/monarchmoney) Python library. Uses a [patched fork](https://github.com/Maninae/monarchmoney) with API domain migration and gql 4.0 compatibility fixes applied.

## License

Non-Commercial Personal Use License — free to use, copy, modify, and share for personal, non-commercial purposes. See [LICENSE](LICENSE) for details.
