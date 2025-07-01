import asyncio
import pytest
import types
from pathlib import Path

# This is a bit of a hack to get the softcosim module in the path
# A proper setup.py or pyproject.toml would handle this better
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from softcosim.engine import CompanySim

@pytest.mark.asyncio
async def test_qa_logs_results(tmp_path: Path, monkeypatch):
    """
    Tests that the QA agent runs and logs the results of the test run.
    """
    # Mock the docker runner to avoid actual docker calls
    def fake_run_pytest(_):
        return "PASS"
    
    # We need to create a fake docker_runner module to monkeypatch
    docker_runner_mock = types.SimpleNamespace(run_pytest=fake_run_pytest)
    sys.modules['softcosim.docker_runner'] = docker_runner_mock
    
    # Speed up the test by removing the sleep
    async def fake_sleep(_):
        pass
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    sim = CompanySim(prompt="Test QA", days=1, root=tmp_path)
    await sim.start()

    qa_log_path = tmp_path / "qa" / "test_log.txt"
    assert qa_log_path.exists()
    
    content = qa_log_path.read_text()
    assert "PASS" in content

    timeline_path = tmp_path / "timeline.md"
    timeline_content = timeline_path.read_text(encoding="utf-8")
    
    assert "QA: Running tests in Docker" in timeline_content
    assert "QA: Syntax check PASS" in timeline_content
