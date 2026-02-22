import os
import logging
import time
from typing import Optional, List, Dict, Any

import requests

from version import APP_VERSION


logger = logging.getLogger("airingdeck.anilist")


class AniListService:
    """Service per interagire con AniList GraphQL API"""
    
    API_URL = "https://graphql.anilist.co"
    DEFAULT_TIMEOUT_SEC = 10.0
    DEFAULT_MIN_INTERVAL_SEC = 2.1
    
    def __init__(self):
        self._token: Optional[str] = None
        self._request_timeout = max(
            1.0,
            self._env_float("AIRINGDECK_ANILIST_TIMEOUT_SEC", self.DEFAULT_TIMEOUT_SEC),
        )
        self._min_request_interval = max(
            0.0,
            self._env_float("AIRINGDECK_ANILIST_MIN_INTERVAL_SEC", self.DEFAULT_MIN_INTERVAL_SEC),
        )
        self._last_request_monotonic = 0.0
        self._user_agent = os.getenv(
            "AIRINGDECK_USER_AGENT",
            f"AiringDeck/{APP_VERSION} (+https://github.com/Pankyop/AiringDeck)",
        )
        logger.info(
            "AniList client configured (timeout=%.1fs, min_interval=%.2fs)",
            self._request_timeout,
            self._min_request_interval,
        )

    @staticmethod
    def _env_float(name: str, default: float) -> float:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            return float(raw.strip())
        except (TypeError, ValueError):
            return default
    
    def set_token(self, token: str):
        """Imposta access token"""
        self._token = token

    def _sleep_backoff(self, attempt_index: int):
        """Small linear backoff between transient retries."""
        time.sleep(1 * (attempt_index + 1))

    def _wait_for_request_slot(self):
        """Apply conservative pacing to stay below AniList rate limits."""
        if self._min_request_interval <= 0:
            return
        now = time.monotonic()
        elapsed = now - self._last_request_monotonic
        wait_time = self._min_request_interval - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

    @staticmethod
    def _header_int(headers: Any, key: str) -> Optional[int]:
        if not headers:
            return None
        value = headers.get(key)
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    def _rate_limit_wait_seconds(self, response: Optional[requests.Response]) -> float:
        if response is None:
            return 5.0

        headers = getattr(response, "headers", None)
        retry_after = self._header_int(headers, "Retry-After")
        if retry_after and retry_after > 0:
            return float(retry_after)

        reset_at = self._header_int(headers, "X-RateLimit-Reset")
        if reset_at:
            delta = reset_at - int(time.time())
            if delta > 0:
                return float(delta)

        return 5.0
    
    def _query(self, query: str, variables: Optional[Dict] = None, retries: int = 3) -> Dict[str, Any]:
        """Esegui query GraphQL con retry su errori transienti e timeout."""
        if not self._token:
            raise Exception("Not authenticated")
        retries = max(1, int(retries))

        headers = {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': self._user_agent,
        }
        
        last_error = None
        for attempt in range(retries):
            try:
                self._wait_for_request_slot()
                self._last_request_monotonic = time.monotonic()
                response = requests.post(
                    self.API_URL,
                    json={'query': query, 'variables': variables or {}},
                    headers=headers,
                    timeout=self._request_timeout,
                )
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("Invalid response payload type")

                if 'errors' in data:
                    message = str(data['errors'][0].get('message', 'GraphQL error'))
                    if "rate limit" in message.lower():
                        raise Exception("HTTP429: Rate limit exceeded")
                    raise Exception(message)

                return data.get('data', {})
            except ValueError:
                last_error = Exception("InvalidResponse: AniList returned invalid JSON")
                logger.warning("API attempt %d/%d failed: invalid JSON payload", attempt + 1, retries)
            except requests.exceptions.Timeout:
                last_error = Exception("Timeout: AniList request timed out")
                logger.warning("API attempt %d/%d timed out", attempt + 1, retries)
            except requests.exceptions.ConnectionError:
                last_error = Exception("ConnectionError: Unable to reach AniList")
                logger.warning("API attempt %d/%d failed: connection error", attempt + 1, retries)
            except requests.exceptions.HTTPError as exc:
                code = exc.response.status_code if exc.response is not None else None
                if code == 401:
                    raise Exception("HTTP401: Not authenticated")
                if code == 429:
                    last_error = Exception("HTTP429: Rate limit exceeded")
                    wait_seconds = self._rate_limit_wait_seconds(exc.response)
                    logger.warning(
                        "API attempt %d/%d failed: rate limit (retry_after=%.1fs)",
                        attempt + 1,
                        retries,
                        wait_seconds,
                    )
                    if attempt < retries - 1:
                        time.sleep(wait_seconds)
                        continue
                elif code is not None and code >= 500:
                    last_error = Exception(f"HTTP{code}: AniList request failed")
                    logger.warning("API attempt %d/%d failed: server error %s", attempt + 1, retries, code)
                else:
                    raise Exception(f"HTTP{code}: AniList request failed")
            except requests.exceptions.RequestException as exc:
                last_error = Exception(f"RequestError: {exc}")
                logger.warning("API attempt %d/%d failed: request error", attempt + 1, retries)
            except Exception as exc:
                # GraphQL / payload errors are non-transient in this context.
                raise exc

            if attempt < retries - 1:
                self._sleep_backoff(attempt)

        raise last_error or Exception("Unknown API error")
    
    def get_viewer_info(self) -> Dict[str, Any]:
        """Ottieni informazioni utente corrente"""
        query = """
        query {
            Viewer {
                id
                name
                avatar {
                    large
                    medium
                }
                statistics {
                    anime {
                        count
                        episodesWatched
                    }
                }
            }
        }
        """
        
        data = self._query(query)
        return data['Viewer']
    
    def get_watching_anime(self, user_id: int) -> List[Dict[str, Any]]:
        """Ottieni lista anime "Watching" dell'utente"""
        query = """
        query ($userId: Int, $status: MediaListStatus) {
            MediaListCollection(userId: $userId, type: ANIME, status: $status) {
                lists {
                    entries {
                        media {
                            id
                            title {
                                romaji
                                english
                                native
                            }
                            coverImage {
                                extraLarge
                                large
                                medium
                            }
                            nextAiringEpisode {
                                episode
                                airingAt
                                timeUntilAiring
                            }
                            genres
                            averageScore
                            siteUrl
                        }
                        progress
                    }
                }
            }
        }
        """
        
        data = self._query(query, {
            'userId': user_id,
            'status': 'CURRENT'
        })
        
        if data['MediaListCollection']['lists']:
            return data['MediaListCollection']['lists'][0]['entries']
        return []
