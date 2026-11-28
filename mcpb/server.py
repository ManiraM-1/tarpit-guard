"""Entry point for the tarpit-guard Claude Desktop extension.

The tarpit_guard package sits next to this file inside the bundle, so it is
importable without installing anything from PyPI.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tarpit_guard.mcp_server import run  # noqa: E402

if __name__ == "__main__":
    run()
