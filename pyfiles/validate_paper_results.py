import sys
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "research_upgrade" / "v3" / "scripts" / "validate_paper_results.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
