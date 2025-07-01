import asyncio
import pytest
from pathlib import Path
import os

# This is a bit of a hack to get the softcosim module in the path
# A proper setup.py or pyproject.toml would handle this better
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from softcosim.engine import CompanySim
from softcosim.llm import chat

@pytest.mark.asyncio
async def test_llm_fake_mode(tmp_path: Path, monkeypatch):
    """
    Tests that the LLM fake mode returns canned responses and zero cost.
    """
    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "1")
    sim = CompanySim(prompt="Test LLM", sim_hours=1, root=tmp_path)
    agent = sim.agents["mgr"]
    reply = await agent.ask_llm("system", "user")
    assert reply == "FAKE-LLM-REPLY"
    assert sim.cost == 0.0

@pytest.mark.asyncio
async def test_llm_real_mode_cost_tracking(tmp_path: Path, monkeypatch):
    """
    Tests that the LLM real mode tracks cost.
    This test will fail if OPENROUTER_API_KEY is not set.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set, skipping real LLM test.")

    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "0")
    sim = CompanySim(prompt="Test LLM", sim_hours=1, root=tmp_path)
    agent = sim.agents["mgr"]
    await agent.ask_llm("system", "user")
    assert sim.cost > 0.0


@pytest.mark.asyncio
async def test_llm_streaming_fake(monkeypatch):
    """Tokens should be yielded when streaming in fake mode."""
    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "1")
    messages = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    stream = await chat("test", messages, stream=True)
    out = ""
    async for token in stream:
        out += token
    assert out == "FAKE-LLM-REPLY"
