from pathlib import Path
from os import path as os_path

def safe_path(root: Path, target: Path) -> Path:
    """
    Resolves a target path relative to a root, ensuring it does not escape the root.
    """
    root = root.resolve()
    p = (root / target).resolve()
    try:
        relative = p.is_relative_to(root)
    except AttributeError:
        # For Python <3.9; use os.path.commonpath as a fallback
        relative = os_path.commonpath([root, p]) == str(root)
    if not relative:
        raise ValueError(f"Path escape blocked: {p} is not within {root}")
    return p

def write(root: Path, rel_path: str, text: str, mode: str = "a"):
    """
    Safely writes text to a file within the root directory.
    """
    p = safe_path(root, Path(rel_path))
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open(mode, encoding="utf-8") as f:
        f.write(text)
