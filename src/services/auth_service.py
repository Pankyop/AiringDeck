from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
import logging
import keyring
from urllib.parse import parse_qs, unquote, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = logging.getLogger("airingdeck.auth")

class AuthService(QObject):
    """Service to handle AniList OAuth via Implicit Grant"""
    
    # Signals
    auth_completed = Signal(str)  # token
    auth_failed = Signal(str)     # error message
    
    # Configuration
    REDIRECT_URI = "http://localhost:8080/callback"
    CLIENT_ID = "34803"
    VERSION = "1.0.6 - token parse hardening"
    KEYRING_SERVICE = "airingdeck"
    LEGACY_KEYRING_SERVICE = "anime-calendar"
    KEYRING_USER = "anilist_token"
    
    def __init__(self):
        super().__init__()
        logger.info("AuthService initialized - VERSION: %s", self.VERSION)
        self._server = None
        self._token = self.get_saved_token()
    
    def _stop_server(self):
        """Stop local server if running"""
        if self._server:
            if self._server.isListening():
                self._server.close()
            self._server.deleteLater()
            self._server = None

    def start_auth_flow(self):
        """Start the OAuth flow"""
        # Ensure any old server is stopped
        self._stop_server()
        
        # Start local TCP server
        self._server = QTcpServer()
        self._server.newConnection.connect(self._handle_connection)
        
        # Listen on ANY (IPv6 + IPv4)
        if not self._server.listen(QHostAddress.Any, 8080):
            logger.error("Failed to start server on Any:8080: %s", self._server.errorString())
            # Fallback to IPv4 only if Any fails
            if not self._server.listen(QHostAddress.AnyIPv4, 8080):
                self.auth_failed.emit("Failed to start local server on port 8080")
                return
        
        logger.info("Server listening on %s:%s", self._server.serverAddress().toString(), self._server.serverPort())
        
        # Construction manual - Semplificata per evitare 'unsupported_grant_type'
        import time
        auth_url = f"https://anilist.co/api/v2/oauth/authorize?client_id={self.CLIENT_ID}&response_type=token&v={int(time.time())}"
        
        logger.info("Opening auth URL")
        QDesktopServices.openUrl(QUrl(auth_url))
    
    def _handle_connection(self):
        """Handle incoming connection from browser"""
        socket = self._server.nextPendingConnection()
        socket.readyRead.connect(lambda: self._read_socket(socket))
    
    def _read_socket(self, socket: QTcpSocket):
        """Read HTTP request from socket"""
        data = socket.readAll().data().decode('utf-8')
        logger.debug("Server received content prefix: %s", data[:100])
        
        # Simple HTTP parsing
        if "GET /callback" in data or "GET / " in data:
            self._send_callback_page(socket)
        elif "GET /submit_token" in data:
            self._handle_token_submission(data, socket)
        else:
            logger.warning("Unhandled request: %s", data.splitlines()[0] if data else "Empty")
            socket.close()
    
    def _send_callback_page(self, socket: QTcpSocket):
        """Serve HTML page to extract hash fragment"""
        html = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Authenticating...</h1>
            <script>
                // Extract token from hash: #access_token=...&token_type=...
                if(window.location.hash) {
                    var hash = window.location.hash.substring(1);
                    var params = new URLSearchParams(hash);
                    var token = params.get('access_token');
                    
                    if(token) {
                        // Send token back to server
                        fetch('/submit_token?token=' + encodeURIComponent(token))
                            .then(() => document.body.innerHTML = '<h1>Login Successful! You can close this window.</h1>')
                            .catch(e => document.body.innerHTML = '<h1>Error sending token.</h1>');
                    } else {
                        document.body.innerHTML = '<h1>Error: No access token found.</h1>';
                    }
                } else {
                    document.body.innerHTML = '<h1>Error: No hash fragment.</h1>';
                }
            </script>
        </body>
        </html>
        """
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"
            f"Content-Length: {len(html)}\r\n"
            "\r\n"
            f"{html}"
        )
        socket.write(response.encode('utf-8'))
        socket.flush()
        socket.disconnectFromHost()
    
    def _handle_token_submission(self, data: str, socket: QTcpSocket):
        """Handle the /submit_token request"""
        # Extract token from query: GET /submit_token?token=XYZ HTTP/1.1
        try:
            logger.info("Parsing token from callback request")
            # First line: GET /submit_token?token=XYZ HTTP/1.1
            request_line = data.split('\n')[0]
            path = request_line.split(' ')[1]
            query = urlparse(path).query
            token = parse_qs(query).get("token", [None])[0]
            token = unquote(token) if token else None
            if not token:
                raise ValueError("Missing token query parameter")
            logger.info("Token successfully parsed")
            
            # Send simple OK response
            response = "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"
            socket.write(response.encode('utf-8'))
            socket.flush()
            socket.disconnectFromHost()
            
            # Save token and emit signal
            self.save_token(token)
            self.auth_completed.emit(token)
            
            # Stop server
            self._server.close()
            self._server = None
            
        except Exception as e:
            logger.error("Error parsing token: %s", e)
            socket.close()
            self.auth_failed.emit("Failed to parse token")

    def save_token(self, token: str):
        """Save token securely"""
        keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USER, token)
        self._token = token
    
    def get_saved_token(self) -> str | None:
        """Get saved token"""
        try:
            token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USER)
            if token:
                return token

            # Backward compatibility: migrate token from legacy keyring service.
            legacy_token = keyring.get_password(self.LEGACY_KEYRING_SERVICE, self.KEYRING_USER)
            if legacy_token:
                self.save_token(legacy_token)
                return legacy_token
            return None
        except Exception as exc:
            logger.warning("Keyring read failed: %s", exc)
            return None
    
    def clear_token(self):
        """Clear saved token"""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USER)
        except Exception as exc:
            logger.debug("Primary keyring delete failed: %s", exc)
        try:
            keyring.delete_password(self.LEGACY_KEYRING_SERVICE, self.KEYRING_USER)
        except Exception as exc:
            logger.debug("Legacy keyring delete failed: %s", exc)
        self._token = None
