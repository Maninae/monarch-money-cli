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
- **Long-lived sessions** — Device UUID + trusted device support for non-expiring tokens

## Quick Start

```bash
git clone https://github.com/Maninae/monarch-money-cli.git
cd monarch-money-cli
pip install -e .
```

```bash
monarch auth login                  # interactive — email, password, MFA, Device UUID
monarch accounts list               # JSON by default
monarch accounts list --format table # human-readable
monarch transactions list --limit 20
monarch cashflow summary
```

## First-Time Setup

`monarch auth login` will prompt for:

1. **Device UUID** — required for long-lived tokens (without it, tokens expire in ~1 hour)
2. **Email** and **Password**
3. **MFA Code** (if MFA is enabled on your account)

### Getting Your Device UUID

1. Log into [app.monarchmoney.com](https://app.monarchmoney.com) in your browser
2. Open DevTools (right-click → Inspect, or `Cmd+Option+I`)
3. Go to the **Console** tab
4. Run: `localStorage.getItem("monarchDeviceUUID")`
5. Copy the UUID string (without quotes)

The UUID is saved to `~/.monarch/config.json` after first login — you won't need to enter it again.

### Why Device UUID?

Monarch Money treats logins without a recognized Device UUID as untrusted and issues tokens that expire in ~1 hour. With the UUID, the server issues non-expiring tokens. See [hammem/monarchmoney#139](https://github.com/hammem/monarchmoney/issues/139) for background.

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
| `~/.monarch/session.json` | Auth token (pickle format) | `600` |
| `~/.monarch/config.json` | Device UUID | `600` |
| `~/.monarch/` | Session directory | `700` |

## Security

- **All credentials are entered interactively** — nothing leaks to shell history or process lists.
- **Session and config files** are created with restricted permissions (`600`). Treat `~/.monarch/` like any credential store.
- **Logging out** (`monarch auth logout`) clears the local session file but does not revoke the token server-side.

## Dependencies

Built on the [monarchmoney](https://github.com/hammem/monarchmoney) Python library. Uses a [patched fork](https://github.com/Maninae/monarchmoney) with API domain migration and gql 4.0 compatibility fixes applied.

## License

Non-Commercial Personal Use License — free to use, copy, modify, and share for personal, non-commercial purposes. See [LICENSE](LICENSE) for details.
