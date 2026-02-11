import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    """Build Windows executable"""
    
    project_root = Path(__file__).parent.parent
    
    PyInstaller.__main__.run([
        str(project_root / 'src' / 'main.py'),
        '--name=AnimeCalendar',
        '--onefile',
        '--windowed',
        # f'--icon={project_root / "resources" / "icons" / "app.ico"}',
        '--add-data=src/ui/qml;ui/qml',
        '--add-data=resources;resources',
        '--hidden-import=PySide6',
        '--hidden-import=requests',
        '--hidden-import=keyring',
        '--clean',
        '--noconfirm',
    ])

if __name__ == '__main__':
    build()
