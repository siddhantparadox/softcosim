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
async def test_developer_creates_hello(tmp_path: Path, monkeypatch):
    """
    Tests that the developer agent creates the hello.py file as instructed by the manager.
    """
    # Speed up the test by removing the sleep
    async def fake_sleep(_):
        pass
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    sim = CompanySim(prompt="HelloWorld", sim_hours=1, root=tmp_path)
    await sim.start()

    hello_path = tmp_path / "src" / "hello.py"
    assert hello_path.exists()
    
    # Check that the file compiles
    import py_compile
    try:
        py_compile.compile(str(hello_path), doraise=True)
    except py_compile.PyCompileError as e:
        pytest.fail(f"hello.py failed to compile: {e}")

    timeline_path = tmp_path / "timeline.md"
    timeline_content = timeline_path.read_text(encoding="utf-8")
    
    assert "Manager: Planning project" in timeline_content
    assert "Dev-A: Writing hello.py" in timeline_content
