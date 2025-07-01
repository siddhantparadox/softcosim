# SoftCoSim

A simulation of a software studio, powered by LLMs.

## High-Level Goals

- A single CLI command kicks off a full “software-studio” simulation.
- All output stays inside one root folder that the user chooses.
- Agents (manager, lead, devs, QA, HR) talk, code, gossip, take breaks, and hit a simulated deadline.
- Every event is streamed live to the terminal and written to markdown / code files in real time.
- The first thing the CLI does is ask for (or read) an OpenRouter API key.
- LLM replies can be streamed token-by-token.

## Tech Stack

| Layer       | Lib / tool                        | Note                                |
| ----------- | --------------------------------- | ----------------------------------- |
| CLI & core  | Python 3.12, `typer`              | Auto-gen help and coloured prompts. |
| LLM calls   | OpenRouter `/v1/chat/completions` | Model name set per agent, token streaming via `aiohttp`. |
| Concurrency | `asyncio`                         | CPU-light, fits CLI use.            |
| Scheduler   | `heapq`, `dataclasses`            | No extra deps.                      |
| Terminal UI | `rich`                            | Progress bars + live tables.        |
| Sandboxing  | Docker + `python:3.12-slim`       | Easy to spin up, predictable.       |
| Testing     | `pytest`, `ruff`, `bandit`        | Run inside the container.           |

## Usage

```bash
softcosim <prompt> --hours 8 --folder ./run1
```

## Development

To set up the development environment, run:

```bash
python -m venv .venv
.venv\Scripts\activate.ps1
pip install -e .[dev]
pytest -q
```
