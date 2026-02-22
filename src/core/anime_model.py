from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Property, Signal

class AnimeModel(QAbstractListModel):
    """Modello ad alte prestazioni per la lista anime"""
    
    # Ruoli per l'accesso ai dati in QML
    MediaRole = Qt.UserRole + 1
    DisplayTitleRole = Qt.UserRole + 2
    AiringTimeRole = Qt.UserRole + 3
    IsTodayRole = Qt.UserRole + 4
    ProgressRole = Qt.UserRole + 5
    RatingDisplayRole = Qt.UserRole + 6
    
    countChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []
        self._signature = ()

    @Property(int, notify=countChanged)
    def count(self):
        return len(self._entries)

    def roleNames(self):
        return {
            self.MediaRole: b"media",
            self.DisplayTitleRole: b"display_title",
            self.AiringTimeRole: b"airing_time_formatted",
            self.IsTodayRole: b"is_today",
            self.ProgressRole: b"progress",
            self.RatingDisplayRole: b"rating_display",
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
        elif role == self.RatingDisplayRole:
            return entry.get('rating_display', "--")
            
        return None

    def update_data(self, new_entries):
        """Aggiorna il modello con nuovi dati"""
        new_signature = tuple(self._entry_key(entry) for entry in new_entries)
        old_count = len(self._entries)
        new_count = len(new_entries)

        # If row identity/order is unchanged, update in-place and notify only role changes.
        if self._signature == new_signature:
            if new_count == 0:
                self._entries = new_entries
                return
            self._entries = new_entries
            top_left = self.index(0, 0)
            bottom_right = self.index(new_count - 1, 0)
            self.dataChanged.emit(
                top_left,
                bottom_right,
                [
                    self.MediaRole,
                    self.DisplayTitleRole,
                    self.AiringTimeRole,
                    self.IsTodayRole,
                    self.ProgressRole,
                    self.RatingDisplayRole,
                ],
            )
            return

        self.beginResetModel()
        self._entries = new_entries
        self._signature = new_signature
        self.endResetModel()
        if old_count != new_count:
            self.countChanged.emit()

    def _entry_key(self, entry):
        media = entry.get("media", {})
        media_id = media.get("id")
        if media_id is not None:
            return media_id
        return id(entry)

    def get_entry(self, row):
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None
