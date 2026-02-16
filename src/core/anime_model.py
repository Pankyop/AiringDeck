from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Property, Signal

class AnimeModel(QAbstractListModel):
    """Modello ad alte prestazioni per la lista anime"""
    
    # Ruoli per l'accesso ai dati in QML
    MediaRole = Qt.UserRole + 1
    DisplayTitleRole = Qt.UserRole + 2
    AiringTimeRole = Qt.UserRole + 3
    IsTodayRole = Qt.UserRole + 4
    ProgressRole = Qt.UserRole + 5
    
    countChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []

    @Property(int, notify=countChanged)
    def count(self):
        return len(self._entries)

    def roleNames(self):
        return {
            self.MediaRole: b"media",
            self.DisplayTitleRole: b"display_title",
            self.AiringTimeRole: b"airing_time_formatted",
            self.IsTodayRole: b"is_today",
            self.ProgressRole: b"progress"
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._entries)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._entries):
            return None
            
        entry = self._entries[index.row()]
        
        if role == self.MediaRole:
            return entry.get('media', {})
        elif role == self.DisplayTitleRole:
            return entry.get('display_title', "Unknown")
        elif role == self.AiringTimeRole:
            return entry.get('airing_time_formatted', "TBA")
        elif role == self.IsTodayRole:
            return entry.get('is_today', False)
        elif role == self.ProgressRole:
            return entry.get('progress', 0)
            
        return None

    def update_data(self, new_entries):
        """Aggiorna il modello con nuovi dati"""
        self.beginResetModel()
        self._entries = new_entries
        self.endResetModel()
        self.countChanged.emit()

    def get_entry(self, row):
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None
