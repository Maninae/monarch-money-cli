<div align="center">

# Monarch Money CLI

Query your finances from the terminal. Accounts, transactions, budgets, cashflow — one command away.

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Non--Commercial-F5A623?style=for-the-badge" alt="License"></a>

</div>

---

- **Full API coverage** — accounts, transactions, budgets, cashflow, categories, tags, recurring, institutions
- **Agent-friendly** — JSON output by default, structured for scripts and AI agents
- **Human-friendly** — `--format table` for readable output, interactive auth with MFA
- **Session persistence** — login once, query anytime

## Quick Start

```bash
git clone https://github.com/Maninae/monarch-money-cli.git
cd monarch-money-cli
pip install -e .
```

```bash
monarch auth login                  # interactive, supports MFA
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

Session tokens are stored in `~/.monarch/session.json` with restricted file permissions (`600`). The session directory is created with `700` permissions.

## Security

- **Use interactive auth when possible.** The `--password` and `--mfa-secret` flags exist for automation but expose credentials in your process list and shell history.
- **Session tokens** are stored locally with restricted permissions. Treat `~/.monarch/` like any credential store.
- **Logging out** clears the local session file but does not revoke the token server-side.

## Dependencies

Built on the [monarchmoney](https://github.com/hammem/monarchmoney) Python library. The upstream PyPI release (`0.1.15`) is currently broken — Monarch rebranded their API domain and the `gql` GraphQL library shipped a breaking change in v4.0. This project uses a [patched fork](https://github.com/Maninae/monarchmoney) with both fixes applied. Will switch back to upstream when a new release ships.

## License

Non-Commercial Personal Use License — free to use, copy, modify, and share for personal, non-commercial purposes. See [LICENSE](LICENSE) for details.
