import requests

from services.anilist_service import AniListService


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.exceptions.HTTPError(f"HTTP {self.status_code}")
            err.response = self
            raise err

    def json(self):
        return self._payload


def test_query_raises_when_not_authenticated():
    svc = AniListService()
    try:
        svc._query("query { Viewer { id } }")
        assert False, "Expected exception"
    except Exception as exc:
        assert "Not authenticated" in str(exc)


def test_query_success(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    def fake_post(url, json, headers, timeout):
        assert "Authorization" in headers
        return _Response({"data": {"Viewer": {"id": 1}}})

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    out = svc._query("query { Viewer { id } }")
    assert out == {"Viewer": {"id": 1}}


def test_query_retries_then_timeout(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        raise requests.exceptions.Timeout("boom")

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    try:
        svc._query("query { Viewer { id } }", retries=2)
        assert False, "Expected timeout exception"
    except Exception as exc:
        assert "Timeout" in str(exc)
        assert attempts["n"] == 2


def test_query_maps_http_status(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    def fake_post(url, json, headers, timeout):
        return _Response({}, status_code=429)

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    try:
        svc._query("query { Viewer { id } }", retries=1)
        assert False, "Expected HTTP 429 mapped error"
    except Exception as exc:
        assert "HTTP429" in str(exc)


def test_get_watching_anime_handles_empty_lists(monkeypatch):
    svc = AniListService()
    monkeypatch.setattr(
        svc,
        "_query",
        lambda query, variables=None, retries=3: {"MediaListCollection": {"lists": []}},
    )

    out = svc.get_watching_anime(10)
    assert out == []


def test_get_viewer_info_returns_viewer_payload(monkeypatch):
    svc = AniListService()
    monkeypatch.setattr(svc, "_query", lambda query, variables=None, retries=3: {"Viewer": {"id": 42, "name": "ketou"}})

    out = svc.get_viewer_info()

    assert out["id"] == 42
    assert out["name"] == "ketou"


def test_get_watching_anime_returns_first_list_entries(monkeypatch):
    svc = AniListService()
    entries = [{"media": {"id": 1}, "progress": 3}]
    monkeypatch.setattr(
        svc,
        "_query",
        lambda query, variables=None, retries=3: {"MediaListCollection": {"lists": [{"entries": entries}]}},
    )

    out = svc.get_watching_anime(99)

    assert out == entries


def test_query_retries_then_connection_error(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        raise requests.exceptions.ConnectionError("offline")

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    try:
        svc._query("query { Viewer { id } }", retries=3)
        assert False, "Expected connection error exception"
    except Exception as exc:
        assert "ConnectionError" in str(exc)
        assert attempts["n"] == 3


def test_query_raises_on_graphql_error_payload(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    def fake_post(url, json, headers, timeout):
        return _Response({"errors": [{"message": "GraphQL exploded"}]})

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)

    try:
        svc._query("query { Viewer { id } }", retries=1)
        assert False, "Expected GraphQL errors payload to raise"
    except Exception as exc:
        assert "GraphQL exploded" in str(exc)


def test_query_recovers_after_single_timeout(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise requests.exceptions.Timeout("temporary timeout")
        return _Response({"data": {"Viewer": {"id": 42}}})

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    out = svc._query("query { Viewer { id } }", retries=3)

    assert out == {"Viewer": {"id": 42}}
    assert attempts["n"] == 2


def test_query_recovers_after_single_http429(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return _Response({}, status_code=429)
        return _Response({"data": {"Viewer": {"id": 7}}})

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    out = svc._query("query { Viewer { id } }", retries=3)

    assert out == {"Viewer": {"id": 7}}
    assert attempts["n"] == 2


def test_query_recovers_after_invalid_json_payload(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    class _BadJsonResponse(_Response):
        def json(self):
            raise ValueError("malformed json")

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return _BadJsonResponse({})
        return _Response({"data": {"Viewer": {"id": 9}}})

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    out = svc._query("query { Viewer { id } }", retries=3)

    assert out == {"Viewer": {"id": 9}}
    assert attempts["n"] == 2


def test_query_does_not_retry_http401(monkeypatch):
    svc = AniListService()
    svc.set_token("tok")

    attempts = {"n": 0}

    def fake_post(url, json, headers, timeout):
        attempts["n"] += 1
        return _Response({}, status_code=401)

    monkeypatch.setattr("services.anilist_service.requests.post", fake_post)
    monkeypatch.setattr(svc, "_sleep_backoff", lambda *_: None)

    try:
        svc._query("query { Viewer { id } }", retries=3)
        assert False, "Expected HTTP401 error"
    except Exception as exc:
        assert "HTTP401" in str(exc)
        assert attempts["n"] == 1


def test_rate_limit_wait_seconds_uses_retry_after_header():
    svc = AniListService()

    class _Resp:
        headers = {"Retry-After": "7"}

    assert svc._rate_limit_wait_seconds(_Resp()) == 7.0


def test_rate_limit_wait_seconds_uses_reset_header(monkeypatch):
    svc = AniListService()

    class _Resp:
        headers = {"X-RateLimit-Reset": "120"}

    monkeypatch.setattr("services.anilist_service.time.time", lambda: 100.0)
    assert svc._rate_limit_wait_seconds(_Resp()) == 20.0
