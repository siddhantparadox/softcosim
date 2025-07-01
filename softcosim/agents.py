from __future__ import annotations
import random
from typing import TYPE_CHECKING
from .fs import write
from .llm import chat

if TYPE_CHECKING:
    from .engine import CompanySim

class Agent:
    model = "mistralai/devstral-small"

    def __init__(self, sim: "CompanySim", name: str):
        self.sim = sim
        self.name = name

    async def act(self):
        ...

    async def ask_llm(self, system_prompt: str, user_prompt: str) -> str:
        msg = [{"role": "system", "content": system_prompt},
               {"role": "user", "content": user_prompt}]
        reply, price, latency = await chat(self.model, msg)
        self.sim.add_cost(price)
        self.sim.log(f"{self.name} LLM call ${price:.4f} ({latency:.2f}s)", kind="INFO")
        return reply

    async def gossip(self):
        prompt = "Write a single, snarky sentence of office gossip."
        line = await self.ask_llm("You are a disgruntled office worker.", prompt)
        self.sim.log(f"{self.name} whispers: '{line}'", kind="GOSSIP")
        self.sim.morale = max(0, self.sim.morale - random.uniform(*self.sim.MORALE_DECAY))
        self.sim._append_gossip(self.name, line)

class Manager(Agent):
    model = "google/gemini-2.5-flash"
    async def act(self):
        self.sim.log(f"{self.name}: Planning project")
        prompt = f"Create a 3-ticket project plan for: {self.sim.prompt}"
        plan = await self.ask_llm("You are a project manager.", prompt)
        self.sim.log(f"Project plan:\n{plan}")
        # schedule developer work at +0.1 h to show causal chain
        self.sim.schedule(0.1, self.sim.agents["dev"].work, desc="Dev writes hello")
        self.sim.schedule(0.2, self.sim.agents["qa"].run_tests, desc="QA run")

def extract_code_block(text: str) -> str:
    """Extracts the first Python code block from a Markdown string."""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text

class Developer(Agent):
    async def work(self):
        self.sim.log(f"{self.name}: Writing hello.py")
        prompt = f"Write a python script that prints 'Hello, SoftCoSim!' for the project: {self.sim.prompt}. Return ONLY the Python code, no markdown or commentary."
        reply = await self.ask_llm("You are a software developer.", prompt)
        code = extract_code_block(reply)
        # The fs.write function handles path creation and ensures it's within the root
        write(self.sim.root, "src/hello.py", code, mode="w")

class QA(Agent):
    async def run_tests(self):
        self.sim.log(f"{self.name}: Running tests in Docker")
        from .docker_runner import run_pytest
        from pathlib import Path
        # We need to mount the whole project, not just the run folder
        project_root = Path(__file__).resolve().parent.parent
        result = run_pytest(str(project_root))
        # summarise pass/fail
        status = "PASS" if result.strip().endswith("PASS") else "FAIL"
        self.sim.log(f"{self.name}: Syntax check {status}")
        # write full log
        write(self.sim.root, "qa/test_log.txt", result, mode="w")
