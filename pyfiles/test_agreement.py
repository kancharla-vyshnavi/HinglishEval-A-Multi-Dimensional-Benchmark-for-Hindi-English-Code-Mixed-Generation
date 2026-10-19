import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from human_validation_app.test_agreement import *

if __name__ == "__main__":
    import unittest
    unittest.main()
