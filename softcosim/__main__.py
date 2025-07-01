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
    prompt: str = typer.Option(None, "--prompt", "-p", help="Project prompt for the team"),
    days: int = typer.Option(None, "--days", "-d", help="Number of days to simulate"),
    budget: float = typer.Option(None, "--budget", "-b", help="LLM budget in USD"),
    folder: Path = typer.Option(..., "--folder", "-f", help="The root folder for the simulation output."),
    start_hour: int = typer.Option(
        None,
        "--start-hour",
        help="Hour the workday starts (0-23)",
    ),
    end_hour: int = typer.Option(
        None,
        "--end-hour",
        help="Hour the workday ends (1-24)",
    ),
    speed: float = typer.Option(
        None,
        "--speed",
        help="Seconds per simulated hour",
    ),
):
    """Kicks off a new software studio simulation."""

    console.print(":wave: Welcome to SoftCoSim!")
    if not prompt:
        prompt = typer.prompt("Project description")
    if days is None:
        days = typer.prompt("Number of days", type=int)
    if budget is None:
        budget = typer.prompt("LLM budget (USD)", type=float)
    if start_hour is None:
        start_hour = typer.prompt("Start hour", type=int)
    if end_hour is None:
        end_hour = typer.prompt("End hour", type=int)
    if speed is None:
        speed = typer.prompt("Seconds per simulated hour", type=float)

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
    sim = CompanySim(
        prompt,
        days,
        folder.resolve(),
        start_hour=start_hour,
        end_hour=end_hour,
        seconds_per_hour=speed,
        budget=budget,
    )
    asyncio.run(sim.start())
    console.print(":white_check_mark: Done.")

if __name__ == "__main__":
    app()
