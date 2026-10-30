"""
Comprehensive guardrail script running linter, format checks, and test suite.
Usage: uv run python scripts/check.py
"""

import subprocess
import sys


def run(cmd: str) -> None:
    print(f"\n[RUNNING] {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[FAILED] Command exited with code {res.returncode}: {cmd}")
        sys.exit(res.returncode)


def main() -> None:
    print("=== PHYS_LIVING_INDEX REPO GUARDRAIL ===")
    run("uv run ruff check src tests")
    run("uv run ruff format --check src tests")
    run("uv run pytest -q")
    print("\n[SUCCESS] All checks and tests passed cleanly!")


if __name__ == "__main__":
    main()
