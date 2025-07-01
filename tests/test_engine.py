import pytest
import asyncio
from pathlib import Path

from softcosim.engine import CompanySim

@pytest.mark.asyncio
async def test_timeline_logs_events(tmp_path: Path, monkeypatch):
    """
    Tests that the engine runs, and logs the initial events to timeline.md.
    """
    # Speed up the test by removing the sleep
    async def fake_sleep(_):
        pass
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    output_dir = tmp_path / "test_run"
    output_dir.mkdir()

    sim = CompanySim(prompt="Test Engine", days=1, root=output_dir)
    await sim.start()
    
    timeline_path = output_dir / "timeline.md"
    assert timeline_path.exists()
    
    content = timeline_path.read_text(encoding="utf-8")
    assert "| Fatigue |" in content
    assert "Manager: Planning project" in content
    assert "Dev-A: Writing hello.py" in content
    assert "Deadline reached – stopping" in content


@pytest.mark.asyncio
async def test_fatigue_decay_and_recovery(tmp_path: Path, monkeypatch):
    async def fake_sleep(_):
        pass
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    sim = CompanySim(prompt="Fatigue", days=1, root=tmp_path)
    await sim.start()

    assert sim.fatigue > 0
    max_fatigue = sim.hours_per_day * sim.FATIGUE_RATE
    assert sim.fatigue < max_fatigue

    timeline_content = (tmp_path / "timeline.md").read_text()
    lines = [
        line
        for line in timeline_content.splitlines()
        if "Coffee break" in line or "Lunch break" in line
    ]
    assert lines
