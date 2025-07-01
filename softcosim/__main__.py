import typer
import os
import asyncio
from pathlib import Path
from rich.console import Console
from .engine import CompanySim

app = typer.Typer(add_completion=False)
console = Console()

def abort(msg: str, code: int = 1):
    print(f"Error: {msg}")
    raise typer.Exit(code)

@app.command()
def run(
    prompt: str = typer.Argument(..., help="Project prompt for the team"),
    hours: int = typer.Option(8, "--hours", "-h", help="The number of simulated hours to run."),
    folder: Path = typer.Option(..., "--folder", "-f", help="The root folder for the simulation output."),
):
    """
    Kicks off a new software studio simulation.
    """
    # 1. Folder guard
    if folder.exists():
        abort(f"Output folder '{folder}' already exists.")
    try:
        folder.mkdir(parents=True, exist_ok=False)
    except Exception as e:
        abort(f"Could not create folder '{folder}': {e}")

    # 2. API-key retrieval
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("OpenRouter API key: ", end="")
        api_key = input()

    if not api_key.strip():
        abort("API key cannot be empty.")
    os.environ["OPENROUTER_API_KEY"] = api_key

    # 3. Kick off simulation
    console.print(":rocket: Launching simulation…")
    sim = CompanySim(prompt, hours, folder.resolve())
    asyncio.run(sim.start())
    console.print(":white_check_mark: Done.")

if __name__ == "__main__":
    app()
