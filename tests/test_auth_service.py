import services.auth_service as auth_module


class _FakeSocket:
    def __init__(self):
        self.written = b""
        self.flushed = False
        self.disconnected = False
        self.closed = False

    def write(self, payload: bytes):
        self.written += payload

    def flush(self):
        self.flushed = True

    def disconnectFromHost(self):
        self.disconnected = True

    def close(self):
        self.closed = True


class _FakeServer:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _SignalProbe:
    def __init__(self):
        self.connected = None

    def connect(self, fn):
        self.connected = fn


class _AddrProbe:
    def toString(self):
        return "0.0.0.0"


class _TcpServerProbe:
    def __init__(self, listen_results):
        self.newConnection = _SignalProbe()
        self._listen_results = list(listen_results)
        self.listen_calls = []
        self._listening = False
        self.closed = False
        self.deleted = False
        self.pending_socket = None

    def listen(self, address, port):
        self.listen_calls.append((address, port))
        result = self._listen_results.pop(0) if self._listen_results else False
        self._listening = bool(result)
        return bool(result)

    def isListening(self):
        return self._listening

    def close(self):
        self.closed = True
        self._listening = False

    def deleteLater(self):
        self.deleted = True

    def errorString(self):
        return "bind failed"

    def serverAddress(self):
        return _AddrProbe()

    def serverPort(self):
        return 8080

    def nextPendingConnection(self):
        return self.pending_socket


class _ReadyReadSocket(_FakeSocket):
    def __init__(self, payload):
        super().__init__()
        self._payload = payload
        self.readyRead = _SignalProbe()

    class _ReadData:
        def __init__(self, payload):
            self._payload = payload

        def data(self):
            return self._payload.encode("utf-8")

    def readAll(self):
        return self._ReadData(self._payload)


def test_get_saved_token_migrates_legacy(monkeypatch):
    calls = []

    def fake_get_password(service, user):
        if service == auth_module.AuthService.KEYRING_SERVICE:
            return None
        if service == auth_module.AuthService.LEGACY_KEYRING_SERVICE:
            return "legacy-token"
        return None

    def fake_set_password(service, user, token):
        calls.append((service, user, token))

    monkeypatch.setattr(auth_module.keyring, "get_password", fake_get_password)
    monkeypatch.setattr(auth_module.keyring, "set_password", fake_set_password)

    svc = auth_module.AuthService()
    assert svc.get_saved_token() == "legacy-token"
    assert len(calls) >= 1
    assert calls[-1] == (
        auth_module.AuthService.KEYRING_SERVICE,
        auth_module.AuthService.KEYRING_USER,
        "legacy-token",
    )


def test_clear_token_deletes_both_services(monkeypatch):
    deleted = []

    def fake_delete_password(service, user):
        deleted.append((service, user))

    monkeypatch.setattr(auth_module.keyring, "delete_password", fake_delete_password)
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)

    svc = auth_module.AuthService()
    svc.clear_token()

    assert (
        auth_module.AuthService.KEYRING_SERVICE,
        auth_module.AuthService.KEYRING_USER,
    ) in deleted
    assert (
        auth_module.AuthService.LEGACY_KEYRING_SERVICE,
        auth_module.AuthService.KEYRING_USER,
    ) in deleted
    assert svc._token is None


def test_handle_token_submission_emits_completed(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    svc._server = _FakeServer()
    fake_socket = _FakeSocket()

    saved = []
    completed = []
    failed = []
    monkeypatch.setattr(svc, "save_token", lambda token: saved.append(token))
    svc.auth_completed.connect(lambda token: completed.append(token))
    svc.auth_failed.connect(lambda msg: failed.append(msg))

    data = "GET /submit_token?token=abc123 HTTP/1.1\r\nHost: localhost\r\n\r\n"
    svc._handle_token_submission(data, fake_socket)

    assert saved == ["abc123"]
    assert completed == ["abc123"]
    assert failed == []
    assert fake_socket.flushed is True
    assert fake_socket.disconnected is True
    assert svc._server is None


def test_handle_token_submission_emits_failed_on_missing_token(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    svc._server = _FakeServer()
    fake_socket = _FakeSocket()

    failed = []
    svc.auth_failed.connect(lambda msg: failed.append(msg))

    data = "GET /submit_token HTTP/1.1\r\nHost: localhost\r\n\r\n"
    svc._handle_token_submission(data, fake_socket)

    assert failed == ["Failed to parse token"]
    assert fake_socket.closed is True


def test_get_saved_token_returns_none_on_keyring_failure(monkeypatch):
    def fake_get_password(service, user):
        raise RuntimeError("keyring down")

    monkeypatch.setattr(auth_module.keyring, "get_password", fake_get_password)
    svc = auth_module.AuthService()
    assert svc.get_saved_token() is None


def test_stop_server_closes_and_clears_reference(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    server = _TcpServerProbe([True])
    server._listening = True
    svc._server = server

    svc._stop_server()

    assert server.closed is True
    assert server.deleted is True
    assert svc._server is None


def test_start_auth_flow_emits_failed_when_binds_fail(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    monkeypatch.setattr(auth_module, "QTcpServer", lambda: _TcpServerProbe([False, False]))
    monkeypatch.setattr(auth_module.QDesktopServices, "openUrl", lambda *_: True)

    svc = auth_module.AuthService()
    failed = []
    svc.auth_failed.connect(lambda msg: failed.append(msg))

    svc.start_auth_flow()

    assert failed == ["Failed to start local server on port 8080"]


def test_start_auth_flow_fallback_ipv4_success_opens_browser(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    server = _TcpServerProbe([False, True])
    monkeypatch.setattr(auth_module, "QTcpServer", lambda: server)
    opened = {"url": None}

    def fake_open(url):
        opened["url"] = url.toString()
        return True

    monkeypatch.setattr(auth_module.QDesktopServices, "openUrl", fake_open)

    svc = auth_module.AuthService()
    svc.start_auth_flow()

    assert len(server.listen_calls) == 2
    assert server.newConnection.connected is not None
    assert opened["url"] is not None
    assert "https://anilist.co/api/v2/oauth/authorize" in opened["url"]


def test_handle_connection_wires_ready_read(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    server = _TcpServerProbe([True])
    sock = _ReadyReadSocket("GET / HTTP/1.1\r\n\r\n")
    server.pending_socket = sock
    svc._server = server

    svc._handle_connection()

    assert sock.readyRead.connected is not None


def test_read_socket_routes_callback_and_submit(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()

    routed = {"callback": 0, "submit": 0}
    monkeypatch.setattr(svc, "_send_callback_page", lambda socket: routed.__setitem__("callback", routed["callback"] + 1))
    monkeypatch.setattr(
        svc,
        "_handle_token_submission",
        lambda data, socket: routed.__setitem__("submit", routed["submit"] + 1),
    )

    svc._read_socket(_ReadyReadSocket("GET /callback HTTP/1.1\r\n\r\n"))
    svc._read_socket(_ReadyReadSocket("GET /submit_token?token=abc HTTP/1.1\r\n\r\n"))

    assert routed["callback"] == 1
    assert routed["submit"] == 1


def test_read_socket_unhandled_request_closes_socket(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    sock = _ReadyReadSocket("GET /unknown HTTP/1.1\r\n\r\n")

    svc._read_socket(sock)

    assert sock.closed is True


def test_send_callback_page_writes_html_response(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    svc = auth_module.AuthService()
    sock = _FakeSocket()

    svc._send_callback_page(sock)

    text = sock.written.decode("utf-8")
    assert "HTTP/1.1 200 OK" in text
    assert "text/html" in text
    assert "Authenticating..." in text
    assert sock.flushed is True
    assert sock.disconnected is True


def test_save_token_updates_keyring_and_memory(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)
    saved = []
    monkeypatch.setattr(auth_module.keyring, "set_password", lambda service, user, token: saved.append((service, user, token)))
    svc = auth_module.AuthService()

    svc.save_token("xyz")

    assert saved[-1] == (
        auth_module.AuthService.KEYRING_SERVICE,
        auth_module.AuthService.KEYRING_USER,
        "xyz",
    )
    assert svc._token == "xyz"


def test_get_saved_token_returns_primary_when_available(monkeypatch):
    monkeypatch.setattr(
        auth_module.keyring,
        "get_password",
        lambda service, user: "primary-token" if service == auth_module.AuthService.KEYRING_SERVICE else None,
    )
    svc = auth_module.AuthService()

    assert svc.get_saved_token() == "primary-token"


def test_clear_token_ignores_delete_exceptions(monkeypatch):
    monkeypatch.setattr(auth_module.AuthService, "get_saved_token", lambda self: None)

    def fake_delete_password(service, user):
        raise RuntimeError("delete failed")

    monkeypatch.setattr(auth_module.keyring, "delete_password", fake_delete_password)
    svc = auth_module.AuthService()
    svc._token = "abc"

    svc.clear_token()

    assert svc._token is None
