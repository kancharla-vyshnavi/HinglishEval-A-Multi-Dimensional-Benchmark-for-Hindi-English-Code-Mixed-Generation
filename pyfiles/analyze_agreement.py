import sys
from pathlib import Path

# Ensure root is in sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_validation_app.analyze_agreement import main

if __name__ == "__main__":
    main()
