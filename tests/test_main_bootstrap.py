from pathlib import Path

import main as main_module


class _FakeMessageBox:
    calls = []

    @classmethod
    def critical(cls, parent, title, message):
        cls.calls.append((title, message))


class _FakeRootContext:
    def __init__(self):
        self.props = {}

    def setContextProperty(self, key, value):
        self.props[key] = value


class _FakeEngine:
    def __init__(self):
        self._ctx = _FakeRootContext()
        self.loaded = []
        self._roots = [object()]

    def rootContext(self):
        return self._ctx

    def load(self, url):
        self.loaded.append(url)

    def rootObjects(self):
        return self._roots


class _FakeApp:
    _instance = None
    set_policy_calls = 0

    class _RoundingPolicy:
        PassThrough = object()

    def __init__(self, argv):
        _FakeApp._instance = self
        self.argv = argv
        self.app_name = ""
        self.org_name = ""
        self.app_version = ""
        self.quit_called = 0

    @classmethod
    def instance(cls):
        return cls._instance

    @classmethod
    def setHighDpiScaleFactorRoundingPolicy(cls, policy):
        cls.set_policy_calls += 1

    def setApplicationName(self, name):
        self.app_name = name

    def setOrganizationName(self, name):
        self.org_name = name

    def setApplicationVersion(self, version):
        self.app_version = version

    def setWindowIcon(self, icon):
        self.icon = icon

    def quit(self):
        self.quit_called += 1

    def exec(self):
        return 0


class _FakeIcon:
    def __init__(self, path):
        self.path = path


class _FakeQTimer:
    calls = []

    @classmethod
    def singleShot(cls, ms, callback):
        cls.calls.append((ms, callback))


class _FakeQuickStyle:
    styles = []

    @classmethod
    def setStyle(cls, style):
        cls.styles.append(style)


class _FakeController:
    def __init__(self, engine):
        self.engine = engine

    def sendTestNotification(self):
        return None


def _setup_common(monkeypatch):
    _FakeMessageBox.calls = []
    _FakeQTimer.calls = []
    _FakeQuickStyle.styles = []
    _FakeApp._instance = None
    _FakeApp.set_policy_calls = 0

    monkeypatch.setattr(main_module, "QApplication", _FakeApp)
    monkeypatch.setattr(main_module, "QMessageBox", _FakeMessageBox)
    monkeypatch.setattr(main_module, "QQmlApplicationEngine", _FakeEngine)
    monkeypatch.setattr(main_module, "QIcon", _FakeIcon)
    monkeypatch.setattr(main_module, "QTimer", _FakeQTimer)
    monkeypatch.setattr(main_module, "QQuickStyle", _FakeQuickStyle)
    monkeypatch.delenv("AIRINGDECK_PROFILE", raising=False)
    monkeypatch.delenv("AIRINGDECK_AUTO_EXIT_MS", raising=False)
    monkeypatch.delenv("AIRINGDECK_TEST_NOTIFICATION_MS", raising=False)


def test_is_truthy_variants():
    assert main_module._is_truthy("1") is True
    assert main_module._is_truthy("true") is True
    assert main_module._is_truthy(" yes ") is True
    assert main_module._is_truthy("on") is True
    assert main_module._is_truthy("0") is False
    assert main_module._is_truthy("no") is False
    assert main_module._is_truthy("") is False
    assert main_module._is_truthy(None) is False


def test_main_returns_minus_one_on_controller_init_error(monkeypatch):
    _setup_common(monkeypatch)

    class _BrokenController:
        def __init__(self, engine):
            raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "AppController", _BrokenController)
    monkeypatch.setattr(main_module, "get_resource_path", lambda rel: Path("resources/icons/app.ico"))

    rc = main_module.main()
    assert rc == -1
    assert _FakeMessageBox.calls
    assert _FakeMessageBox.calls[-1][0] == "Init Error"


def test_main_returns_minus_one_when_qml_missing(monkeypatch):
    _setup_common(monkeypatch)
    monkeypatch.setattr(main_module, "AppController", _FakeController)

    def fake_resource(rel):
        if rel.endswith("app.ico"):
            return Path("resources/icons/app.ico")
        return Path("does-not-exist.qml")

    monkeypatch.setattr(main_module, "get_resource_path", fake_resource)

    rc = main_module.main()
    assert rc == -1
    assert any(title == "Resource Error" for title, _ in _FakeMessageBox.calls)


def test_main_returns_minus_one_when_engine_has_no_roots(monkeypatch):
    _setup_common(monkeypatch)

    class _EmptyRootEngine(_FakeEngine):
        def __init__(self):
            super().__init__()
            self._roots = []

    monkeypatch.setattr(main_module, "QQmlApplicationEngine", _EmptyRootEngine)
    monkeypatch.setattr(main_module, "AppController", _FakeController)

    qml = Path("src/ui/qml/BootShell.qml")
    monkeypatch.setattr(main_module, "get_resource_path", lambda rel: qml)

    rc = main_module.main()
    assert rc == -1
    assert any(title == "QML Error" for title, _ in _FakeMessageBox.calls)


def test_main_schedules_auto_exit_and_test_notification(monkeypatch):
    _setup_common(monkeypatch)
    monkeypatch.setattr(main_module, "AppController", _FakeController)
    monkeypatch.setenv("AIRINGDECK_PROFILE", "1")
    monkeypatch.setenv("AIRINGDECK_AUTO_EXIT_MS", "5000")
    monkeypatch.setenv("AIRINGDECK_TEST_NOTIFICATION_MS", "6000")

    qml = Path("src/ui/qml/BootShell.qml")
    monkeypatch.setattr(main_module, "get_resource_path", lambda rel: qml)

    rc = main_module.main()
    assert rc == 0
    assert _FakeQuickStyle.styles == ["Basic"]
    assert _FakeApp.set_policy_calls == 1
    assert _FakeApp.instance().app_name == "AiringDeck [DEV-PROFILE]"
    assert [ms for ms, _ in _FakeQTimer.calls] == [5000, 6000]
