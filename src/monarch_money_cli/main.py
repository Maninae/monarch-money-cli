"""
Monarch Money CLI - Comprehensive CLI for Monarch Money
"""

import typer

from monarch_money_cli.commands import accounts, auth, budgets, cashflow, categories, institutions, recurring, tags, transactions

app = typer.Typer(
    name="monarch",
    help="Comprehensive CLI for Monarch Money - full API coverage for agents and humans.",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(accounts.app, name="accounts", help="Account management")
app.add_typer(transactions.app, name="transactions", help="Transaction management")
app.add_typer(budgets.app, name="budgets", help="Budget management")
app.add_typer(cashflow.app, name="cashflow", help="Cashflow analysis")
app.add_typer(categories.app, name="categories", help="Category management")
app.add_typer(tags.app, name="tags", help="Tag management")
app.add_typer(recurring.app, name="recurring", help="Recurring transactions")
app.add_typer(institutions.app, name="institutions", help="Linked institutions")


if __name__ == "__main__":
    app()
