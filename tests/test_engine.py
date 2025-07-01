import pytest
import asyncio
from typer.testing import CliRunner
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

    sim = CompanySim(prompt="Test Engine", sim_hours=8, root=output_dir)
    await sim.start()
    
    timeline_path = output_dir / "timeline.md"
    assert timeline_path.exists()
    
    content = timeline_path.read_text(encoding="utf-8")
    assert "Manager: Planning project" in content
    assert "Dev-A: Writing hello.py" in content
    assert "Deadline reached – stopping" in content
