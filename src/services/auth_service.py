from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QTcpServer, QHostAddress
import keyring
from urllib.parse import urlparse, parse_qs
from typing import Optional

class AuthService(QObject):
    """Service per gestire OAuth AniList"""
    
    # Signals
    auth_completed = Signal(str)  # token
    auth_failed = Signal(str)     # error message
    
    CLIENT_ID = "YOUR_ANILIST_CLIENT_ID"  # TODO: Configurare
    REDIRECT_URI = "http://localhost:8080/callback"
    
    def __init__(self):
        super().__init__()
        self._server: Optional[QTcpServer] = None
        self._token: Optional[str] = None
    
    def start_auth_flow(self):
        """Avvia OAuth flow"""
        # Start local server per callback
        self._server = QTcpServer()
        self._server.newConnection.connect(self._handle_callback)
        
        if not self._server.listen(QHostAddress.LocalHost, 8080):
            self.auth_failed.emit("Failed to start local server")
            return
        
        # Apri browser per OAuth
        auth_url = (
            f"https://anilist.co/api/v2/oauth/authorize?"
            f"client_id={self.CLIENT_ID}&"
            f"redirect_uri={self.REDIRECT_URI}&"
            f"response_type=token"
        )
        
        QDesktopServices.openUrl(QUrl(auth_url))
    
    def _handle_callback(self):
        """Gestisci callback OAuth"""
        # TODO: Implementare parsing token dal callback
        pass
    
    def save_token(self, token: str):
        """Salva token in modo sicuro"""
        keyring.set_password("anime-calendar", "anilist_token", token)
        self._token = token
    
    def get_saved_token(self) -> Optional[str]:
        """Recupera token salvato"""
        try:
            return keyring.get_password("anime-calendar", "anilist_token")
        except:
            return None
    
    def clear_token(self):
        """Cancella token"""
        try:
            keyring.delete_password("anime-calendar", "anilist_token")
        except:
            pass
        self._token = None
