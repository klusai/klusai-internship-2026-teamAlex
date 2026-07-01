"""conftest.py – add the buggy source roots to sys.path so pytest can import them."""
import sys
import os

# Root of Alex Ghiurau's ex1_agent_sdk (contains app/ and buggy/ packages)
_GHIURAU_SDK = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..",  # up to klusai-internship-2026/
    "Alex Ghiurau", "claude-agent-labs", "ex1_agent_sdk",
)
_GHIURAU_SDK = os.path.abspath(_GHIURAU_SDK)

if _GHIURAU_SDK not in sys.path:
    sys.path.insert(0, _GHIURAU_SDK)
