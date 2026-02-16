from datetime import datetime
import logging
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool, QSettings, QTimer
from PySide6.QtQml import QQmlApplicationEngine
from services.auth_service import AuthService
from services.anilist_service import AniListService
from core.worker import Worker
from core.anime_model import AnimeModel
from core.native_accel import filter_entries, is_native_available
from version import APP_VERSION


logger = logging.getLogger("airingdeck.controller")

class AppController(QObject):
    """Main application controller - Bridge tra Python e QML"""
    
    # Signals
    authenticated = Signal(bool)
    userInfoChanged = Signal()
    animeListChanged = Signal()
    isLoadingChanged = Signal()
    statusMessageChanged = Signal()
    selectedAnimeChanged = Signal()
    dailyCountsChanged = Signal()
    filterTextChanged = Signal()
    useEnglishTitleChanged = Signal()
    
    def __init__(self, engine: QQmlApplicationEngine):
        super().__init__()
        self._engine = engine
        self._is_authenticated = False
        self._is_loading = False
        self._status_message = ""
        self._user_info = {"avatar": "https://s4.anilist.co/file/anilistcdn/user/avatar/large/default.png", "name": ""}
        self._selected_anime = None
        self._filter_text = ""
        self._pending_filter_text = ""
        self._anime_by_id = {}
        
        # High-performance Models
        self._all_anime_model = AnimeModel(self)
        self._day_models = [AnimeModel(self) for _ in range(7)]
        
        # Cache for performance
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        
        # Thread pool
        self._thread_pool = QThreadPool()
        logger.info("Multithreading with maximum %d threads", self._thread_pool.maxThreadCount())
        logger.info("Native filter acceleration: %s", "enabled" if is_native_available() else "fallback python")

        # Persistent Settings
        self._settings = QSettings("AiringDeck", "AiringDeck")
        self._use_english_title = self._settings.value("use_english_title", False, type=bool)
        
        # Calendar State
        self._daily_counts = [0] * 7
        self._full_anime_list = [] # Store original non-filtered list
        
        # Countdown Timer (Update every minute)
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(60000) # 60 seconds
        self._update_timer.timeout.connect(self._update_countdowns)
        self._update_timer.start()

        # Debounced filter updates to reduce model churn while typing.
        self._filter_update_timer = QTimer(self)
        self._filter_update_timer.setSingleShot(True)
        self._filter_update_timer.setInterval(140)
        self._filter_update_timer.timeout.connect(self._apply_pending_filter)
        
        # Initialize services
        self._auth_service = AuthService()
        self._anilist_service = AniListService()
        
        # Connect signals
        self._auth_service.auth_completed.connect(self._on_auth_completed)
        self._auth_service.auth_failed.connect(self._on_auth_failed)
        
        # Lazy initialization via explicit call
        # No heavy work in __init__

    @Slot()
    def initialize(self):
        """Heavy initialization triggered after UI is visible"""
        logger.info("Starting lazy initialization...")
        
        # Check initial state
        saved_token = self._auth_service.get_saved_token()
        if saved_token:
            logger.info("Found saved token, validating...")
            self._anilist_service.set_token(saved_token)
            
            # Load offline cache first for instant UI
            self._load_offline_cache()
            
            # Then fetch fresh data (Non-blocking)
            self._fetch_user_info()
        else:
            self._set_loading(False, "Pronto")

    def _load_offline_cache(self):
        """Load cached data from past sessions"""
        import json
        
        # Load User Info
        cached_user = self._settings.value("cached_user_info")
        if cached_user:
            try:
                self._user_info = json.loads(cached_user)
                self._is_authenticated = True
                self.authenticated.emit(True)
                self.userInfoChanged.emit()
            except (TypeError, ValueError) as exc:
                logger.warning("Ignoring invalid cached user info: %s", exc)
                
        # Load Anime List
        cached_list = self._settings.value("cached_anime_list")
        if cached_list:
            try:
                anime_data = json.loads(cached_list)
                self._on_anime_list_result(anime_data, from_cache=True)
            except (TypeError, ValueError) as exc:
                logger.warning("Ignoring invalid cached anime list: %s", exc)

    def _save_offline_cache(self):
        """Save current state to persistent storage"""
        import json
        self._settings.setValue("cached_user_info", json.dumps(self._user_info))
        self._settings.setValue("cached_anime_list", json.dumps(self._full_anime_list))

    def _set_loading(self, loading: bool, message: str = ""):
        self._is_loading = loading
        self._status_message = message
        self.isLoadingChanged.emit()
        self.statusMessageChanged.emit()

    def _on_auth_completed(self, token: str):
        """Handle successful authentication"""
        logger.info("Auth completed")
        self._anilist_service.set_token(token)
        self._fetch_user_info()
    
    def _on_auth_failed(self, error: str):
        """Handle authentication failure"""
        logger.warning("Auth failed: %s", error)
        self._set_loading(False, f"Login failed: {error}")
        
    def _fetch_user_info(self):
        """Fetch user info from AniList (Async)"""
        self._set_loading(True, "Fetching user profile...")
        
        worker = Worker(self._anilist_service.get_viewer_info)
        worker.signals.result.connect(self._on_user_info_result)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _on_user_info_result(self, user):
        """Handle user info result"""
        if user:
            self._user_info = {
                "name": user["name"],
                "avatar": user["avatar"]["large"],
                "id": user["id"]
            }
            self._is_authenticated = True
            self.authenticated.emit(True)
            self.userInfoChanged.emit()
            self._save_offline_cache()
            
            avatar_url = self.userAvatar
            self._set_loading(False, f"Logged in as {user['name']} (Avatar URL set)")
            logger.info("Logged in as %s, avatar=%s", user["name"], avatar_url)
            
            # Fetch watching list
            self.syncAnimeList()
        else:
            self._set_loading(False, "Failed to load profile")

    def _extract_error_text(self, err) -> str:
        """Normalize worker error payloads to readable text."""
        if isinstance(err, tuple) and len(err) >= 2:
            return f"{err[0]}: {err[1]}"
        return str(err)

    def _on_error(self, err):
        """Handle worker error"""
        err_text = self._extract_error_text(err)
        logger.error("Worker error: %s", err_text)

        lower = err_text.lower()
        if "timeout" in lower:
            message = "Request timeout. Check connection and retry."
        elif "connectionerror" in lower or "unable to reach" in lower:
            message = "Network unavailable. Check internet connection."
        elif "http429" in lower or "rate limit" in lower:
            message = "AniList rate limit reached. Retry in a moment."
        elif "http401" in lower or "not authenticated" in lower:
            message = "Session expired. Please login again."
        else:
            message = "Unexpected error while syncing data."

        self._set_loading(False, message)
        # If this was a token error, we might want to logout
        if "http401" in lower or "not authenticated" in lower:
            self.logout()

    # Properties
    @Property(bool, notify=authenticated)
    def isAuthenticated(self):
        return self._is_authenticated
        
    @Property(bool, notify=isLoadingChanged)
    def isLoading(self):
        return self._is_loading

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message
    
    @Property('QVariantMap', notify=userInfoChanged)
    def userInfo(self):
        return self._user_info
    
    @Property(QObject, notify=animeListChanged)
    def allAnimeModel(self):
        return self._all_anime_model

    @Property('QVariantList', notify=animeListChanged)
    def dayModels(self):
        return self._day_models

    @Property(str, notify=filterTextChanged)
    def filterText(self):
        return self._filter_text

    @filterText.setter
    def filterText(self, value):
        self.setFilterText(value)

    @Slot(str)
    def setFilterText(self, value):
        value = value or ""
        self._pending_filter_text = value
        self._filter_update_timer.start()

    def _apply_pending_filter(self):
        if self._filter_text == self._pending_filter_text:
            return
        self._filter_text = self._pending_filter_text
        self._update_ui_models()
        self.filterTextChanged.emit()
        self.animeListChanged.emit()

    @Property('QVariantList', notify=dailyCountsChanged)
    def dailyCounts(self):
        return self._daily_counts
    
    @Property('QVariantMap', notify=selectedAnimeChanged)
    def selectedAnime(self):
        return self._selected_anime if self._selected_anime else {}

    @Property(bool, notify=useEnglishTitleChanged)
    def useEnglishTitle(self):
        return self._use_english_title

    @useEnglishTitle.setter
    def useEnglishTitle(self, value):
        if self._use_english_title != value:
            self._use_english_title = value
            self._settings.setValue("use_english_title", value)
            
            # Recalculate all titles immediately
            self._update_countdowns() 
            
            # Emit signals for UI components
            self.useEnglishTitleChanged.emit()
            self.selectedAnimeChanged.emit() # Refresh sidebar

    @Property(str, notify=userInfoChanged)
    def userAvatar(self):
        return self._user_info.get("avatar", "https://s4.anilist.co/file/anilistcdn/user/avatar/large/default.png")

    @Property(str, constant=True)
    def qtVersion(self):
        from PySide6.QtCore import qVersion
        return qVersion()

    @Property(str, constant=True)
    def appVersion(self):
        return APP_VERSION
    
    # Slots (callable from QML)
    @Slot()
    def login(self):
        """Trigger AniList OAuth login"""
        logger.info("Login requested")
        self._set_loading(True, "Waiting for browser login...")
        self._auth_service.start_auth_flow()
    
    @Slot()
    def logout(self):
        """Logout user"""
        logger.info("Logout requested")
        self._auth_service.clear_token()
        self._anilist_service.set_token("")
        
        self._is_authenticated = False
        self._user_info = {}
        self._full_anime_list = []
        self._anime_by_id = {}
        self._selected_anime = None
        self._daily_counts = [0] * 7
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        self._update_ui_models()
        
        self.authenticated.emit(False)
        self.userInfoChanged.emit()
        self.selectedAnimeChanged.emit()
        self.dailyCountsChanged.emit()
        self.animeListChanged.emit()
        self._set_loading(False, "Logged out")
    
    @Slot()
    def syncAnimeList(self):
        """Sync anime list from AniList"""
        logger.info("Sync anime list requested")
        if not self._is_authenticated:
            return

        user_id = self._user_info.get("id")
        if not user_id:
            return
            
        self._set_loading(True, "Syncing anime list...")
        worker = Worker(self._anilist_service.get_watching_anime, user_id)
        worker.signals.result.connect(self._on_anime_list_result)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)
    
    @Slot(int)
    def selectAnime(self, anime_id: int):
        """Select an anime to show details"""
        logger.debug("Selecting anime ID: %d", anime_id)
        selected = self._anime_by_id.get(anime_id)
        if selected is None:
            return
        self._selected_anime = selected
        self.selectedAnimeChanged.emit()

    def _get_display_title(self, media):
        """Standardized title selection based on settings"""
        titles = media.get('title', {})
        if self._use_english_title:
            return titles.get('english') or titles.get('romaji') or "Unknown Title"
        return titles.get('romaji') or titles.get('english') or "Unknown Title"

    def _format_countdown(self, airing_at):
        """Format countdown with support for days, hours, minutes"""
        now = datetime.now()
        dt = datetime.fromtimestamp(airing_at)
        diff = dt - now
        
        time_str = dt.strftime("%H:%M")
        seconds = diff.total_seconds()
        
        if seconds <= -3600: # Over an hour ago
            return f"Aired {time_str}"
        elif seconds <= 0: # Within the last hour
            return "Airing Now"
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{time_str} (in {days}d {hours}h)"
        elif hours > 0:
            return f"{time_str} (in {hours}h {minutes}m)"
        else:
            return f"{time_str} (in {minutes}m)"

    def _update_countdowns(self):
        """Timer callback to refresh countdown strings"""
        if not self._full_anime_list:
            return
            
        any_changed = False
        for entry in self._full_anime_list:
            media = entry.get('media', {})
            airing = media.get('nextAiringEpisode')
            
            # Update Titles (in case setting changed)
            new_title = self._get_display_title(media)
            if entry.get('display_title') != new_title:
                entry['display_title'] = new_title
                any_changed = True

            # Update Countdown
            if airing:
                new_countdown = self._format_countdown(airing['airingAt'])
                if entry.get('airing_time_formatted') != new_countdown:
                    entry['airing_time_formatted'] = new_countdown
                    any_changed = True

        if any_changed:
            self._update_ui_models()
            self.animeListChanged.emit()

    def _update_ui_models(self):
        """Sync Python data to QML models with filtering"""
        query = self._filter_text.lower().strip()
        
        # Update Individual Day Models
        for i in range(7):
            day_list = self._weekly_schedule_cache[i]
            if query:
                day_list = filter_entries(day_list, query)
            self._day_models[i].update_data(day_list)

        # Update Full Model (Airing Only)
        full_airing = self._full_airing_entries
        if query:
            full_airing = filter_entries(full_airing, query)
        self._all_anime_model.update_data(full_airing)

    def _on_anime_list_result(self, anime_list, from_cache=False):
        """Handle anime list result and process for calendar"""
        self._full_anime_list = anime_list
        self._anime_by_id = {}
        self._daily_counts = [0] * 7
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        
        today_weekday = datetime.now().weekday()
        
        for entry in self._full_anime_list:
            media = entry.get('media', {})
            media_id = media.get("id")
            if media_id is not None:
                self._anime_by_id[media_id] = entry
            airing = media.get('nextAiringEpisode')
            
            # Centralize Title
            entry['display_title'] = self._get_display_title(media)
            titles = media.get("title", {})
            romaji = titles.get("romaji") or ""
            english = titles.get("english") or ""
            entry["_search_blob"] = f"{romaji} {english}".lower()
            
            if airing:
                airing_at = airing['airingAt']
                dt = datetime.fromtimestamp(airing_at)
                weekday = dt.weekday()
                
                entry['calendar_day'] = weekday
                entry['is_today'] = (weekday == today_weekday)
                entry['airing_time_formatted'] = self._format_countdown(airing_at)
                
                self._daily_counts[weekday] += 1
                self._weekly_schedule_cache[weekday].append(entry)
                self._full_airing_entries.append(entry)
            else:
                entry['calendar_day'] = -1
                entry['airing_time_formatted'] = "TBA"
                entry['is_today'] = False

        if not from_cache:
            self._save_offline_cache()

        self._update_ui_models()
        self.dailyCountsChanged.emit()
        self.animeListChanged.emit()
        self._set_loading(False, f"Synced {len(anime_list)} anime")
        logger.info("Synced %d anime. Day counts: %s", len(anime_list), self._daily_counts)
