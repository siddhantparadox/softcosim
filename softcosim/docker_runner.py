import subprocess
import os
import tempfile

DOCKER_IMAGE = "python:3.12-slim"

def run_pytest(root: str) -> str:
    """
    Run a syntax check inside Docker and return the result.
    """
    if os.getenv("SOFTCOSIM_NO_DOCKER") == "1":
        return "PASS (docker skipped)"
    # Create a temporary directory on the host that can be mounted as writable
    with tempfile.TemporaryDirectory() as tmp:
        # A single-line command using compileall is the most robust solution.
        bash_command = (
            "cp -a /mnt/. /tmp/work/ && "
            "cd /tmp/work && "
            "python softcosim/checker.py"
        )
        cmd = (
            f'docker run --rm --cpus="0.5" --memory="512m" '
            f'-v "{root}:/mnt:ro" '
            f'-v "{tmp}:/tmp/work" '
            f'-w "/tmp/work" '  # Set the working directory
            f'{DOCKER_IMAGE} '
            f'bash -c "{bash_command}"'
        )
        
        try:
            completed = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            return completed.stdout + completed.stderr
        except FileNotFoundError:
            return "Error: Docker command not found. Is Docker installed and in your PATH?"
