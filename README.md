# Anime Calendar Qt

Desktop application nativa per tracking anime episode releases con AniList integration.

## 🚀 Features

- ✅ Qt 6.7 native application
- ✅ AniList OAuth authentication
- ✅ Calendar view of airing episodes
- ✅ Episode tracking and notifications
- ✅ Modern QML UI
- ✅ Low memory footprint (~50MB)
- ✅ Windows native .exe

## 🛠️ Tech Stack

- **UI Framework**: Qt 6.7 (PySide6)
- **UI Language**: QML (declarative)
- **Backend**: Python 3.11+
- **API**: AniList GraphQL
- **Packaging**: PyInstaller
- **Secure Storage**: keyring

## 📦 Development Setup

### Prerequisites
- Python 3.11 or higher
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Development

```bash
python src/main.py
```

### Build .exe

```bash
python scripts/build_windows.py
```

Output: `dist/AnimeCalendar.exe`

## 📁 Project Structure

```
anime-calendar-qt/
├── src/
│   ├── main.py                 # Entry point
│   ├── core/
│   │   └── app_controller.py   # Main controller
│   ├── services/
│   │   ├── anilist_service.py  # AniList API
│   │   └── auth_service.py     # OAuth
│   ├── models/                 # Data models
│   └── ui/
│       └── qml/                # QML UI files
│           ├── main.qml
│           └── components/
├── resources/
│   ├── icons/
│   ├── images/
│   └── fonts/
├── scripts/
│   └── build_windows.py        # Build script
├── requirements.txt
└── README.md
```

## 🎨 UI Architecture

- **QML**: Declarative UI (similar to React)
- **Python Backend**: Business logic & API calls
- **Qt Signals/Slots**: Communication between QML ↔ Python
- **Property Bindings**: Reactive data binding

## 📝 License

MIT
