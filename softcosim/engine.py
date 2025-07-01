import asyncio
import heapq
import time
import random
from pathlib import Path
from rich.console import Console
from .agents import Manager, Developer, QA


class Event:
    __slots__ = ("t", "fn", "desc")
    def __init__(self, t: float, fn, desc: str = ""):
        self.t, self.fn, self.desc = t, fn, desc
    def __lt__(self, other):  # heapq uses this for ordering
        return self.t < other.t

class CompanySim:
    def __init__(
        self,
        prompt: str,
        days: int,
        root: Path,
        *,
        start_hour: int = 9,
        end_hour: int = 17,
        seconds_per_hour: float = 1.0,
        budget: float = 0.5,
    ):
        self.prompt = prompt
        self.days = days
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.hours_per_day = end_hour - start_hour
        self.total_hours = self.hours_per_day * days
        self.root = root
        self.seconds_per_hour = seconds_per_hour
        self.console = Console()
        self.now = 0.0  # simulated hour float
        self.events: list[Event] = []
        self.start_real = time.perf_counter()
        self.timeline_path = self.root / "timeline.md"
        self.gossip_path = self.root / "gossip.md"
        self.morale = 75.0
        self.MORALE_DECAY = (1.0, 3.0)
        self.cost = 0.0
        self.budget = budget
        self.agents = {
            "mgr": Manager(self, "Manager"),
            "dev": Developer(self, "Dev-A"),
            "qa": QA(self, "QA"),
        }

    async def start(self):
        self._prepare_fs()
        self._schedule_initial_events()
        await self._run_loop()

    def _prepare_fs(self):
        self.timeline_path.write_text(
            "# Timeline\n\n| Sim Time | Kind | Message | Morale | Cost |\n|:---:|:---|:---|:---:|:---:|\n"
        )
        self.gossip_path.write_text(
            "# Gossip Log\n\n| Sim Time | Speaker | Line |\n|:---:|:---|:---|\n"
        )

    def log(self, msg, kind="INFO"):
        line_console = f"[{self.now:0.2f}] {kind} | {msg} | Morale {self.morale:05.1f} | Cost ${self.cost:.4f}"
        line_file = f"| {self.now:0.2f} | {kind} | {msg} | {self.morale:0.1f} | ${self.cost:.4f} |\n"
        self.console.print(line_console)
        with self.timeline_path.open("a", encoding="utf-8") as f:
            f.write(line_file)

    def add_cost(self, delta: float):
        self.cost += delta
        if self.cost > self.budget:
            self.log("Budget exceeded – halting simulation", kind="INFO")
            self.events.clear()

    def _append_gossip(self, speaker: str, line: str):
        with self.gossip_path.open("a", encoding="utf-8") as f:
            f.write(f"| {self.now:0.2f} | {speaker} | {line} |\n")

    def coffee_break(self):
        self.morale = min(100.0, self.morale + 5)
        self.log("Coffee break", kind="EVENT")

    def team_meeting(self):
        self.morale = max(0.0, self.morale - 5)
        self.log("Team meeting", kind="EVENT")

    def schedule(self, delay_hr: float, fn, desc=""):
        heapq.heappush(self.events, Event(self.now + delay_hr, fn, desc))

    def _schedule_initial_events(self):
        self.schedule(0, self.agents["mgr"].act, "Manager kickoff")

        for day in range(self.days):
            base = day * self.hours_per_day

            # daily coffee break and meeting
            coffee = base + (10 - self.start_hour)
            meeting = base + (15 - self.start_hour)
            if 0 <= coffee <= self.total_hours:
                self.schedule(coffee, self.coffee_break, "Coffee break")
            if 0 <= meeting <= self.total_hours:
                self.schedule(meeting, self.team_meeting, "Team meeting")

            # gossip every half hour of work time
            t = base + 0.5
            end = base + self.hours_per_day
            while t < end:
                agent = random.choice(list(self.agents.values()))
                self.schedule(t, agent.gossip, f"{agent.name} gossips")
                t += 0.5

        self.schedule(self.total_hours, lambda: self.log("Deadline reached – stopping"))

    async def _run_loop(self):
        while self.events:
            evt = heapq.heappop(self.events)
            if evt.t > self.total_hours:
                break

            target_real = self.start_real + (evt.t * self.seconds_per_hour)
            to_sleep = target_real - time.perf_counter()
            if to_sleep > 0:
                await asyncio.sleep(to_sleep)

            self.now = evt.t
            if asyncio.iscoroutinefunction(evt.fn):
                await evt.fn()
            else:
                res = evt.fn()
                if asyncio.iscoroutine(res):
                    await res
