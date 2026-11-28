"""Run the bundled tarpit-guard detector. Standard library only, no network.

Usage: python3 tarpit_check.py <file-or-folder> [--json] [--quiet] [--threshold N]
Exit code 0: nothing flagged. 1: at least one file is a tarpit. 2: bad path.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tarpit_guard.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
