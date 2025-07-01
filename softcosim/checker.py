"""
Offline syntax checker for SoftCoSim.

Executed inside the Docker sandbox by the QA agent.  It recursively
byte-compiles every Python source file under the current working
directory.  Exit status 0  → PASS,  exit status 1  → FAIL.
"""

import compileall
import sys

if __name__ == "__main__":
    ok = compileall.compile_dir(".", quiet=1, force=True)
    if ok:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)
