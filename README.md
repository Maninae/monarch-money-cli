<div align="center">
  
  # Monarch Money CLI 🦋
  
  **Your finances at your fingertips** — a comprehensive CLI for Monarch Money
  
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Non--Commercial-F5A623?style=for-the-badge" alt="License"></a>
  
</div>

---

Monarch Money CLI brings the full power of [Monarch Money](https://www.monarchmoney.com/) to your terminal. Query accounts, transactions, budgets, and cashflow — perfect for automation, AI agents, or humans who prefer the command line.

Built on the excellent [monarchmoney](https://github.com/hammem/monarchmoney) Python library. Tested against `monarchmoney==0.1.15` — newer versions may introduce breaking changes.

## ✨ Features

- **Full API coverage** — accounts, transactions, budgets, cashflow, categories, tags
- **Agent-friendly** — JSON output by default, quiet mode for scripts  
- **Human-friendly** — table format, interactive auth with MFA support
- **Session persistence** — login once, query forever

## 📦 Installation

```bash
# From source
git clone https://github.com/Maninae/monarch-money-cli.git
cd monarch-money-cli
pip install -e .

# Or via pip (once published)
pip install monarch-money-cli
```

## 🚀 Quick Start

```bash
# Authenticate (interactive, supports MFA)
monarch auth login

# Check auth status
monarch auth status

# List all accounts
monarch accounts list

# Get recent transactions
monarch transactions list --limit 50

# Check budgets
monarch budgets list
```

## 📖 Commands

### Authentication

```bash
monarch auth login      # Interactive login with MFA support
monarch auth logout     # Clear saved session
monarch auth status     # Check authentication status
```

### Accounts

```bash
monarch accounts list                    # List all accounts
monarch accounts get <id>                # Get account details
monarch accounts history <id>            # Get account balance history
monarch accounts refresh                 # Trigger sync with institutions
monarch accounts create                  # Create manual account
monarch accounts update <id>             # Update account settings
monarch accounts delete <id>             # Delete an account
```

### Transactions

```bash
monarch transactions list                # List recent transactions
monarch transactions get <id>            # Get transaction details
monarch transactions create              # Create a transaction
monarch transactions update <id>         # Update a transaction
monarch transactions delete <id>         # Delete a transaction
monarch transactions splits <id>         # View/manage splits
```

### Budgets

```bash
monarch budgets list                     # List all budgets (⚠ currently broken upstream)
monarch budgets set <category> <amount>  # Set budget amount
```

### Cashflow

```bash
monarch cashflow summary                 # Income/expense/savings summary
monarch cashflow details                 # Detailed cashflow by category
```

### Categories & Tags

```bash
monarch categories list                  # List all categories
monarch categories create <name>         # Create a category
monarch categories delete <id>           # Delete a category

monarch tags list                        # List all tags
monarch tags create <name>               # Create a tag
```

### Recurring Transactions

```bash
monarch recurring list                   # List recurring transactions
```

### Institutions

```bash
monarch institutions list                # List linked institutions
```

## 🎨 Output Formats

```bash
# JSON (default, agent-friendly)
monarch accounts list

# Table format (human-friendly)
monarch accounts list --format table

# Quiet (minimal output)
monarch accounts list --quiet
```

## ⚙️ Configuration

Session tokens are stored in `~/.monarch/session.json` with restricted file permissions (`600`).

## 🔒 Security Notes

- **Interactive auth is recommended.** The `--password` and `--mfa-secret` flags are available for automation but expose credentials in your process list and shell history. Use the interactive prompt when possible.
- **Session tokens** are stored locally in `~/.monarch/` with restricted permissions. Treat this directory like any credential store — don't share or back it up to public locations.
- **Logging out** clears the local session file but does not revoke the token server-side.

## 📄 License

Non-Commercial Personal Use License — free to use, copy, modify, and share for personal, non-commercial purposes. See [LICENSE](LICENSE) for details.
