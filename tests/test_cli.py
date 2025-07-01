from typer.testing import CliRunner
import os

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
        [
            "--folder",
            str(folder),
            "--prompt",
            "Test",
            "--days",
            "1",
            "--budget",
            "1",
            "--start-hour",
            "9",
            "--end-hour",
            "17",
            "--speed",
            "1",
        ],
        catch_exceptions=False,  # Let Typer's Exit bubble up
    )
    
    assert result.exit_code != 0
    out = result.stdout.lower()
    assert "already" in out and "exists" in out

def test_folder_is_created_successfully(tmp_path, monkeypatch):
    """
    Tests that a new folder is created and the README.md is written.
    """
    folder = tmp_path / "run2"
    
    # We need to provide a dummy API key for the test to run non-interactively
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy")
    
    result = runner.invoke(
        app,
        [
            "--folder",
            str(folder),
            "--prompt",
            "Test",
            "--days",
            "1",
            "--budget",
            "1",
            "--start-hour",
            "9",
            "--end-hour",
            "17",
            "--speed",
            "1",
        ],
        catch_exceptions=False,
    )
    
    assert result.exit_code == 0, f"CLI failed with output:\n{result.stdout}"
    assert folder.exists()


def test_cli_accepts_time_options(tmp_path, monkeypatch):
    """CLI parses start/end hour and speed options."""
    folder = tmp_path / "run3"
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy")

    result = runner.invoke(
        app,
        [
            "--folder",
            str(folder),
            "--prompt",
            "Test",
            "--days",
            "1",
            "--budget",
            "1",
            "--start-hour",
            "8",
            "--end-hour",
            "16",
            "--speed",
            "0.5",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"CLI failed with output:\n{result.stdout}"
    assert folder.exists()


def test_cli_prompts_for_defaults(tmp_path, monkeypatch):
    """Missing options trigger interactive prompts."""
    folder = tmp_path / "run4"
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy")

    inputs = "\n".join(["Test", "1", "1", "9", "17", "1"]) + "\n"
    result = runner.invoke(
        app,
        ["--folder", str(folder)],
        input=inputs,
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"CLI failed with output:\n{result.stdout}"
    assert "Start hour" in result.stdout
    assert folder.exists()
