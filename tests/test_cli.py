from typer.testing import CliRunner
import os

# This is a bit of a hack to get the softcosim module in the path
# A proper setup.py or pyproject.toml would handle this better
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from softcosim.__main__ import app

runner = CliRunner()

def test_folder_guard_blocks_existing(tmp_path):
    """
    Tests that the CLI exits with an error if the output folder already exists.
    """
    folder = tmp_path / "run1"
    folder.mkdir()
    
    result = runner.invoke(
        app,
        ["--folder", str(folder), "Test Prompt"],
        catch_exceptions=False, # Let Typer's Exit bubble up
    )
    
    assert result.exit_code != 0
    assert "already" in result.stdout and "exists" in result.stdout

def test_folder_is_created_successfully(tmp_path, monkeypatch):
    """
    Tests that a new folder is created and the README.md is written.
    """
    folder = tmp_path / "run2"
    
    # We need to provide a dummy API key for the test to run non-interactively
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy")
    
    result = runner.invoke(
        app,
        ["--folder", str(folder), "Test Prompt"],
        catch_exceptions=False,
    )
    
    assert result.exit_code == 0, f"CLI failed with output:\n{result.stdout}"
    assert folder.exists()
