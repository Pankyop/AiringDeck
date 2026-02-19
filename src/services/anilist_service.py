import requests
import logging
import time
from typing import Optional, List, Dict, Any


logger = logging.getLogger("airingdeck.anilist")


class AniListService:
    """Service per interagire con AniList GraphQL API"""
    
    API_URL = "https://graphql.anilist.co"
    
    def __init__(self):
        self._token: Optional[str] = None
    
    def set_token(self, token: str):
        """Imposta access token"""
        self._token = token

    def _sleep_backoff(self, attempt_index: int):
        """Small linear backoff between transient retries."""
        time.sleep(1 * (attempt_index + 1))
    
    def _query(self, query: str, variables: Optional[Dict] = None, retries: int = 3) -> Dict[str, Any]:
        """Esegui query GraphQL con retry su errori transienti e timeout."""
        if not self._token:
            raise Exception("Not authenticated")
        retries = max(1, int(retries))

        headers = {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        last_error = None
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.API_URL,
                    json={'query': query, 'variables': variables or {}},
                    headers=headers,
                    timeout=10  # 10 second timeout
                )
                response.raise_for_status()
                data = response.json()

                if 'errors' in data:
                    raise Exception(data['errors'][0]['message'])

                return data.get('data', {})
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
                    logger.warning("API attempt %d/%d failed: rate limit", attempt + 1, retries)
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
