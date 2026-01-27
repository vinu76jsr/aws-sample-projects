#!/usr/bin/env python3
"""
Command Line Interface for Polls DynamoDB.

This CLI helps you learn DynamoDB by interacting with the polls data
directly from the command line.

Usage:
    python cli.py --help
    python cli.py init          # Create table
    python cli.py seed          # Add sample data
    python cli.py list          # List all polls
    python cli.py show <id>     # Show poll details
    python cli.py vote <id>     # Vote on a poll
    python cli.py create        # Create a new poll
    python cli.py delete <id>   # Delete a poll
    python cli.py scan          # Scan entire table (learning)
    python cli.py reset         # Delete and recreate table
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from db import create_table, delete_table, table_exists
from models import Poll, Choice, batch_create_poll_with_choices, scan_all_items

console = Console()


@click.group()
def cli():
    """Polls DynamoDB CLI - Learn DynamoDB with a polls application."""
    pass


@cli.command()
def init():
    """Initialize the DynamoDB table."""
    if table_exists():
        console.print("[yellow]Table already exists![/yellow]")
    else:
        create_table()
        console.print("[green]Table created successfully![/green]")


@cli.command()
def seed():
    """Seed the database with sample polls."""
    if not table_exists():
        console.print("[red]Table does not exist. Run 'init' first.[/red]")
        return

    sample_polls = [
        {
            "question": "What's your favorite programming language?",
            "choices": ["Python", "JavaScript", "Go", "Rust", "TypeScript"]
        },
        {
            "question": "Which cloud provider do you prefer?",
            "choices": ["AWS", "Google Cloud", "Azure", "DigitalOcean"]
        },
        {
            "question": "What's your preferred database type?",
            "choices": ["SQL (PostgreSQL/MySQL)", "NoSQL (MongoDB/DynamoDB)", "Graph (Neo4j)", "Time Series (InfluxDB)"]
        },
        {
            "question": "How do you prefer to deploy applications?",
            "choices": ["Containers (Docker/K8s)", "Serverless (Lambda)", "VMs (EC2)", "PaaS (Heroku/Railway)"]
        },
    ]

    for poll_data in sample_polls:
        poll = batch_create_poll_with_choices(
            poll_data["question"],
            poll_data["choices"]
        )
        console.print(f"[green]Created poll:[/green] {poll.question_text[:50]}...")

    console.print(f"\n[green]Seeded {len(sample_polls)} polls![/green]")


@cli.command("list")
def list_polls():
    """List all polls."""
    if not table_exists():
        console.print("[red]Table does not exist. Run 'init' first.[/red]")
        return

    polls = Poll.get_all()

    if not polls:
        console.print("[yellow]No polls found.[/yellow]")
        return

    table = Table(title="All Polls")
    table.add_column("ID", style="cyan")
    table.add_column("Question", style="white")
    table.add_column("Date", style="green")

    for poll in polls:
        table.add_row(
            poll.poll_id,
            poll.question_text[:50] + ("..." if len(poll.question_text) > 50 else ""),
            poll.pub_date[:10]
        )

    console.print(table)


@cli.command()
@click.argument("poll_id")
def show(poll_id):
    """Show poll details with choices and votes."""
    poll = Poll.get(poll_id)

    if not poll:
        console.print(f"[red]Poll '{poll_id}' not found.[/red]")
        return

    choices = poll.get_choices()
    total_votes = sum(c.votes for c in choices)

    # Create results table
    table = Table(title=f"Poll: {poll.question_text}")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Choice", style="white")
    table.add_column("Votes", style="green", justify="right")
    table.add_column("Percentage", style="yellow", justify="right")

    for i, choice in enumerate(choices, 1):
        pct = (choice.votes / total_votes * 100) if total_votes > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(
            str(i),
            choice.choice_text,
            str(choice.votes),
            f"{pct:.1f}% {bar}"
        )

    console.print(table)
    console.print(f"\n[dim]Total votes: {total_votes}[/dim]")
    console.print(f"[dim]Poll ID: {poll.poll_id}[/dim]")


@cli.command()
@click.argument("poll_id")
def vote(poll_id):
    """Vote on a poll interactively."""
    poll = Poll.get(poll_id)

    if not poll:
        console.print(f"[red]Poll '{poll_id}' not found.[/red]")
        return

    choices = poll.get_choices()

    console.print(Panel(poll.question_text, title="Question"))
    console.print("\nChoices:")

    for i, choice in enumerate(choices, 1):
        console.print(f"  {i}. {choice.choice_text}")

    console.print()
    selection = click.prompt("Enter your choice (number)", type=int)

    if selection < 1 or selection > len(choices):
        console.print("[red]Invalid selection.[/red]")
        return

    selected_choice = choices[selection - 1]
    selected_choice.vote()

    console.print(f"\n[green]Vote recorded for: {selected_choice.choice_text}[/green]")
    console.print(f"[dim]New vote count: {selected_choice.votes}[/dim]")


@cli.command()
def create():
    """Create a new poll interactively."""
    if not table_exists():
        console.print("[red]Table does not exist. Run 'init' first.[/red]")
        return

    question = click.prompt("Enter the poll question")
    console.print("[dim]Enter choices (one per line, empty line to finish):[/dim]")

    choices = []
    while True:
        choice = click.prompt("", default="", show_default=False)
        if not choice:
            break
        choices.append(choice)

    if len(choices) < 2:
        console.print("[red]At least 2 choices are required.[/red]")
        return

    poll = batch_create_poll_with_choices(question, choices)
    console.print(f"\n[green]Poll created![/green]")
    console.print(f"[dim]Poll ID: {poll.poll_id}[/dim]")


@cli.command()
@click.argument("poll_id")
@click.confirmation_option(prompt="Are you sure you want to delete this poll?")
def delete(poll_id):
    """Delete a poll."""
    poll = Poll.get(poll_id)

    if not poll:
        console.print(f"[red]Poll '{poll_id}' not found.[/red]")
        return

    poll.delete()
    console.print(f"[green]Poll '{poll_id}' deleted.[/green]")


@cli.command()
def scan():
    """
    Scan entire table (learning demonstration).

    WARNING: In production, scan() is expensive and should be avoided.
    Use query() with proper key conditions instead.
    """
    if not table_exists():
        console.print("[red]Table does not exist. Run 'init' first.[/red]")
        return

    console.print(Panel(
        "[yellow]WARNING:[/yellow] scan() reads EVERY item in the table.\n"
        "This is expensive and should be avoided in production.\n"
        "Use query() with proper key conditions instead.",
        title="DynamoDB Learning Note"
    ))

    items = scan_all_items()

    table = Table(title=f"All Items in Table ({len(items)} items)")
    table.add_column("PK", style="cyan")
    table.add_column("SK", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Data", style="white")

    for item in items:
        data_preview = str({
            k: v for k, v in item.items()
            if k not in ["PK", "SK", "type", "GSI1PK", "GSI1SK"]
        })[:50]

        table.add_row(
            item.get("PK", ""),
            item.get("SK", ""),
            item.get("type", ""),
            data_preview + "..."
        )

    console.print(table)


@cli.command()
@click.confirmation_option(prompt="This will delete ALL data. Are you sure?")
def reset():
    """Delete and recreate the table."""
    if table_exists():
        console.print("[yellow]Deleting table...[/yellow]")
        delete_table()

    console.print("[yellow]Creating table...[/yellow]")
    create_table()
    console.print("[green]Table reset complete![/green]")


@cli.command()
def info():
    """Show DynamoDB learning information."""
    info_text = """
[bold cyan]DynamoDB Key Concepts:[/bold cyan]

[yellow]1. Primary Key Types:[/yellow]
   • Simple: Partition Key only (PK)
   • Composite: Partition Key + Sort Key (PK + SK)

[yellow]2. Single-Table Design:[/yellow]
   This app uses single-table design where:
   • PK="POLLS", SK="POLL#<id>" → Poll index entries
   • PK="POLL#<id>", SK="METADATA" → Poll details
   • PK="POLL#<id>", SK="CHOICE#<id>" → Choices

[yellow]3. Operations:[/yellow]
   • put_item: Create/replace item
   • get_item: Read by primary key (fast!)
   • update_item: Partial updates
   • delete_item: Remove item
   • query: Find items by partition key (efficient)
   • scan: Read all items (expensive, avoid!)

[yellow]4. Best Practices:[/yellow]
   • Design for access patterns first
   • Use query() instead of scan()
   • Use GSI for additional access patterns
   • Use atomic counters for votes/counts
   • Batch operations for multiple writes

[yellow]5. Cost Model:[/yellow]
   • Pay per read/write capacity or on-demand
   • Reads: 4KB per RCU (eventually consistent)
   • Writes: 1KB per WCU
   • Scans consume capacity for ALL items read
    """
    console.print(Panel(info_text, title="DynamoDB Learning Guide"))


if __name__ == "__main__":
    cli()