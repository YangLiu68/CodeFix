import typer
from rich.console import Console
from rich.markdown import Markdown
import sys

from agent.controller import AgentController

app = typer.Typer(help="CLI Coding Agent – your AI pair programmer in the terminal.")
console = Console()
agent = AgentController()


@app.command()
def chat():
    """Start an interactive chat session with the agent."""
    console.print(
        f"[bold blue]CLI Coding Agent Ready.[/bold blue] "
        f"(Model: [bold green]{agent.model}[/bold green])"
    )
    console.print("Type [bold]exit[/bold] or [bold]quit[/bold] to end. "
                  "Commands: [bold]/map[/bold]  [bold]/clear[/bold]  "
                  "[bold]/fix [task] --test [cmd][/bold]\n")

    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]")
            if not user_input.strip():
                continue
            if user_input.lower() in ["exit", "quit"]:
                console.print("[dim]Goodbye![/dim]")
                break

            console.print("[bold blue]Agent:[/bold blue] ")

            # ── Stream chunks directly — no markdown re-rendering per char ──
            buffer = ""
            for chunk in agent.process_query(user_input):
                # Print each chunk immediately as plain text
                print(chunk, end="", flush=True)
                buffer += chunk

            # Move to a new line after streaming ends
            print("\n")

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'exit' to quit.[/dim]")


if __name__ == "__main__":
    app()
