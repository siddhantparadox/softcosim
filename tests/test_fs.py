import pytest
from pathlib import Path
import tempfile
import os

# This is a bit of a hack to get the softcosim module in the path
# A proper setup.py or pyproject.toml would handle this better
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from softcosim.fs import safe_path

def test_safe_path_allows_valid_paths():
    """
    Tests that safe_path correctly resolves paths that are within the root directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        
        # Test a direct child
        target1 = Path("file.txt")
        assert safe_path(root, target1) == root / target1

        # Test a nested child
        target2 = Path("subdir/file.txt")
        assert safe_path(root, target2) == root / target2

        # Test a path that uses '.'
        target3 = Path("./subdir/../file.txt")
        assert safe_path(root, target3) == root / "file.txt"

def test_safe_path_blocks_escape_attempts():
    """
    Tests that safe_path raises a ValueError for paths that try to escape the root.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir).resolve()
        
        # Test basic parent directory escape
        with pytest.raises(ValueError):
            safe_path(root, Path("../file.txt"))

        # Test more complex escape
        with pytest.raises(ValueError):
            safe_path(root, Path("subdir/../../file.txt"))
            
        # Test with an absolute path outside the root
        other_dir = Path(tempfile.gettempdir()).resolve()
        if other_dir != root:
             with pytest.raises(ValueError):
                safe_path(root, other_dir / "file.txt")

def test_safe_path_with_real_directories():
    """
    Tests safe_path against the current working directory structure.
    """
    # Note: This test is less robust as it depends on the execution environment,
    # but it's a good sanity check.
    root = Path.cwd()
    
    # Should be safe
    assert safe_path(root, Path("softcosim/fs.py"))
    
    # Should be unsafe
    with pytest.raises(ValueError):
        safe_path(root, Path("../some_other_project"))
