import requests
from typing import Optional, List, Dict, Any

class AniListService:
    """Service per interagire con AniList GraphQL API"""
    
    API_URL = "https://graphql.anilist.co"
    
    def __init__(self):
        self._token: Optional[str] = None
    
    def set_token(self, token: str):
        """Imposta access token"""
        self._token = token
    
    def _query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Esegui query GraphQL"""
        if not self._token:
            raise Exception("Not authenticated")
        
        headers = {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        response = requests.post(
            self.API_URL,
            json={'query': query, 'variables': variables or {}},
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        
        return data['data']
    
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
