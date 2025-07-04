import pytest
from pathlib import Path
import os

from softcosim.engine import CompanySim

@pytest.mark.asyncio
async def test_llm_fake_mode(tmp_path: Path, monkeypatch):
    """
    Tests that the LLM fake mode returns canned responses and zero cost.
    """
    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "1")
    sim = CompanySim(prompt="Test LLM", days=1, root=tmp_path)
    agent = sim.agents["mgr"]
    reply = await agent.ask_llm("system", "user")
    assert reply == "FAKE-LLM-REPLY"
    assert sim.cost == 0.0


@pytest.mark.asyncio
async def test_llm_fake_stream_mode(tmp_path: Path, monkeypatch):
    """Streaming mode should also return the fake reply."""
    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "1")
    from softcosim.llm import chat
    msg = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    reply, cost, latency = await chat("model", msg, stream=True)
    assert reply == "FAKE-LLM-REPLY"
    assert cost == 0.0

@pytest.mark.asyncio
async def test_llm_real_mode_cost_tracking(tmp_path: Path, monkeypatch):
    """
    Tests that the LLM real mode tracks cost.
    This test will fail if OPENROUTER_API_KEY is not set.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set, skipping real LLM test.")

    monkeypatch.setenv("SOFTCOSIM_FAKE_LLM", "0")
    sim = CompanySim(prompt="Test LLM", days=1, root=tmp_path)
    agent = sim.agents["mgr"]
    await agent.ask_llm("system", "user")
    assert sim.cost > 0.0
