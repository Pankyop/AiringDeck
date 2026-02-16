import requests
import logging
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
    
    def _query(self, query: str, variables: Optional[Dict] = None, retries: int = 3) -> Dict[str, Any]:
        """Esegui query GraphQL con retry logic e timeout"""
        if not self._token:
            raise Exception("Not authenticated")
        
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
                    timeout=10 # 10 second timeout
                )
                
                response.raise_for_status()
                data = response.json()
                
                if 'errors' in data:
                    raise Exception(data['errors'][0]['message'])
                
                return data['data']
            except (requests.exceptions.RequestException, Exception) as e:
                last_error = e
                logger.warning("API attempt %d failed: %s", attempt + 1, e)
                if attempt < retries - 1:
                    import time
                    time.sleep(1 * (attempt + 1)) # Simple backoff

        if isinstance(last_error, requests.exceptions.Timeout):
            raise Exception("Timeout: AniList request timed out")
        if isinstance(last_error, requests.exceptions.ConnectionError):
            raise Exception("ConnectionError: Unable to reach AniList")
        if isinstance(last_error, requests.exceptions.HTTPError) and last_error.response is not None:
            code = last_error.response.status_code
            if code == 401:
                raise Exception("HTTP401: Not authenticated")
            if code == 429:
                raise Exception("HTTP429: Rate limit exceeded")
            raise Exception(f"HTTP{code}: AniList request failed")

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
