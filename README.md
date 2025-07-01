# SoftCoSim

A simulation of a small software studio powered by LLMs.

## High-Level Goals

- A single CLI command kicks off a full "software-studio" simulation.
- All output stays inside one root folder chosen by the user.
- Agents (manager, developer, QA) talk, code, gossip and hit a simulated deadline.
- Every event is streamed live to the terminal and written to files.
- The CLI first asks for (or reads) an OpenRouter API key.

## Tech Stack

| Layer       | Lib / tool                        | Notes                                  |
| ----------- | --------------------------------- | -------------------------------------- |
| CLI & core  | Python 3.12, `typer`              | Auto-generated help, coloured prompts. |
| LLM calls   | OpenRouter `/v1/chat/completions` | Model name set per agent.              |
| Concurrency | `asyncio`                         | CPU-light, fits CLI use.               |
| Scheduler   | `heapq`, `dataclasses`            | No extra deps.                         |
| Terminal UI | `rich`                            | Progress bars & live tables.           |
| Sandboxing  | Docker + `python:3.12-slim`       | Easy to spin up, predictable.          |
| Testing     | `pytest`, `ruff`, `bandit`        | Run inside the container.              |

## Usage

After installing the package you can start a simulation with:

```bash
softcosim "Build a to‑do app" --days 2 --folder ./run1
```

The command will prompt for an API key if `OPENROUTER_API_KEY` is not already set
in the environment. Output files such as `timeline.md` and `gossip.md` will be
created inside the folder you specify. To speed up the simulation, pass the
`--speed` option where the value is the number of real seconds per simulated
hour. For example, `--speed 2` runs at 30&nbsp;minutes per second.

## Development

1. Create a virtual environment and install the dev extras.

   **Bash**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

   **PowerShell**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e .[dev]
   ```

2. Run linters and the test suite:

   ```bash
   ruff .
   bandit -r softcosim
   pytest
   ```

Tests use fake LLM responses and skip Docker by default (via environment
variables in `pyproject.toml`).
