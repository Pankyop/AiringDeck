import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

_APP = None


def pytest_sessionstart(session):
    # Ensure Qt objects can be created in tests.
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
