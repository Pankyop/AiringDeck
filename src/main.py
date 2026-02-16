import sys
import os
import ctypes
import logging
from time import perf_counter
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtQuickControls2 import QQuickStyle

# Import controllers
from core.app_controller import AppController
from version import APP_VERSION


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("airingdeck.main")


def _is_truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent / relative_path

def main():
    profiling_mode = _is_truthy(os.getenv("AIRINGDECK_PROFILE"))
    auto_exit_ms = int(os.getenv("AIRINGDECK_AUTO_EXIT_MS", "0") or "0")

    # Set AppUserModelID for Windows Taskbar consistency
    if os.name == 'nt':
        try:
            myappid = u"com.antigravity.airingdeck.v3"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.warning("Failed to set AppUserModelID: %s", e)

    # Set style to Basic to allow full customization
    QQuickStyle.setStyle("Basic")

    # Enable High DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AiringDeck [DEV-PROFILE]" if profiling_mode else "AiringDeck")
    app.setOrganizationName("AiringDeck")
    app.setApplicationVersion(APP_VERSION)
    
    # Set app icon with robust pathing
    icon_path = get_resource_path("resources/icons/app.ico")
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create app controller
    try:
        controller = AppController(engine)
        engine.rootContext().setContextProperty("appController", controller)
    except Exception as e:
        QMessageBox.critical(None, "Init Error", f"Failed to initialize controller: {str(e)}")
        return -1
    
    # Load BootShell (Instant UI)
    start_time = perf_counter()
    
    qml_file = get_resource_path("src/ui/qml/BootShell.qml")
    if not qml_file.exists():
        QMessageBox.critical(None, "Resource Error", f"Critical file not found: {qml_file}")
        return -1
        
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    logger.info("BootShell loaded in %dms", int((perf_counter() - start_time) * 1000))
    
    if not engine.rootObjects():
        QMessageBox.critical(None, "QML Error", "Failed to load QML objects. Check logs for details.")
        return -1

    if auto_exit_ms > 0:
        logger.info("Auto-exit timer enabled: %dms", auto_exit_ms)
        QTimer.singleShot(auto_exit_ms, app.quit)

    # Run application
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Final safety net for top-level crashes
        logger.exception("FATAL ERROR")
        # If QApplication was already created, try to show a message
        if QApplication.instance():
            QMessageBox.critical(None, "Fatal Error", str(e))
        sys.exit(1)
