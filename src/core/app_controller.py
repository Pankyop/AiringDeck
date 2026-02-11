from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QQmlApplicationEngine

class AppController(QObject):
    """Main application controller - Bridge tra Python e QML"""
    
    # Signals
    authenticated = Signal(bool)
    userInfoChanged = Signal()
    animeListChanged = Signal()
    
    def __init__(self, engine: QQmlApplicationEngine):
        super().__init__()
        self._engine = engine
        self._is_authenticated = False
        self._user_info = {}
        self._anime_list = []
        
        # Initialize services (will be implemented later)
        # self._auth_service = AuthService()
        # self._anilist_service = AniListService()
    
    # Properties
    @Property(bool, notify=authenticated)
    def isAuthenticated(self):
        return self._is_authenticated
    
    @Property('QVariantMap', notify=userInfoChanged)
    def userInfo(self):
        return self._user_info
    
    @Property('QVariantList', notify=animeListChanged)
    def animeList(self):
        return self._anime_list
    
    # Slots (callable from QML)
    @Slot()
    def login(self):
        """Trigger AniList OAuth login"""
        print("Login requested")
        # TODO: Implement OAuth flow
        self._is_authenticated = True
        self.authenticated.emit(True)
    
    @Slot()
    def logout(self):
        """Logout user"""
        print("Logout requested")
        self._is_authenticated = False
        self._user_info = {}
        self._anime_list = []
        self.authenticated.emit(False)
        self.userInfoChanged.emit()
        self.animeListChanged.emit()
    
    @Slot()
    def syncAnimeList(self):
        """Sync anime list from AniList"""
        print("Sync anime list requested")
        # TODO: Implement sync
        self.animeListChanged.emit()
    
    @Slot(str, result=str)
    def getPreference(self, key: str) -> str:
        """Get user preference"""
        # TODO: Implement preference storage
        return ""
    
    @Slot(str, str)
    def setPreference(self, key: str, value: str):
        """Set user preference"""
        # TODO: Implement preference storage
        print(f"Set preference: {key} = {value}")
