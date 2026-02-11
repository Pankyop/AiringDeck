import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon

# Import controllers
from core.app_controller import AppController

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Anime Calendar")
    app.setOrganizationName("AnimeCalendar")
    app.setApplicationVersion("1.0.0")
    
    # Set app icon
    icon_path = Path(__file__).parent.parent / "resources" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create app controller
    controller = AppController(engine)
    
    # Register context properties
    engine.rootContext().setContextProperty("appController", controller)
    
    # Load main QML
    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("Error: Failed to load QML")
        return -1
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
