import asyncio
import pytest
from pathlib import Path

# This is a bit of a hack to get the softcosim module in the path
# A proper setup.py or pyproject.toml would handle this better
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from softcosim.engine import CompanySim

@pytest.mark.asyncio
async def test_gossip_and_morale(tmp_path: Path, monkeypatch):
    """
    Tests that gossip events are logged and that morale decreases.
    """
    # Speed up the test by removing the sleep
    async def fake_sleep(_):
        pass
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    sim = CompanySim(prompt="Test Gossip", days=1, root=tmp_path)
    initial_morale = sim.morale
    await sim.start()

    # Check that morale has decreased
    assert sim.morale < initial_morale

    # Check that gossip.md was created and has content
    gossip_path = tmp_path / "gossip.md"
    assert gossip_path.exists()
    gossip_content = gossip_path.read_text()
    assert "| Manager |" in gossip_content or "| Dev-A |" in gossip_content or "| QA |" in gossip_content

    # Check that timeline.md has morale column
    timeline_path = tmp_path / "timeline.md"
    timeline_content = timeline_path.read_text()
    assert "| Morale |" in timeline_content
    assert "| Fatigue |" in timeline_content
    assert "GOSSIP" in timeline_content
