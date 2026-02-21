from datetime import datetime
import logging
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool, QSettings, QTimer, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtGui import QDesktopServices
from services.auth_service import AuthService
from services.anilist_service import AniListService
from services.update_service import UpdateService
from core.worker import Worker
from core.anime_model import AnimeModel
from core.native_accel import filter_entries_advanced, is_native_available
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
    selectedGenreChanged = Signal()
    onlyTodayChanged = Signal()
    minScoreChanged = Signal()
    sortFieldChanged = Signal()
    sortAscendingChanged = Signal()
    availableGenresChanged = Signal()
    appLanguageChanged = Signal()
    notificationsEnabledChanged = Signal()
    notificationLeadMinutesChanged = Signal()
    updateAvailableChanged = Signal()
    updateInfoChanged = Signal()
    
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
        self._selected_genre = "All genres"
        self._only_today = False
        self._min_score = 0
        self._sort_field = "airing_time"
        self._sort_ascending = True
        self._available_genres = ["All genres"]
        self._app_language = "it"
        self._notifications_enabled = True
        self._notification_lead_minutes = 15
        self._notified_episode_times = {}
        self._last_notification_media_id = None
        self._tray_icon = None
        self._anime_by_id = {}
        self._sync_in_progress = False
        self._sync_queued = False
        self._sync_retry_attempts = 0
        self._max_sync_retry_attempts = 1
        self._update_available = False
        self._update_check_in_progress = False
        self._update_latest_version = ""
        self._update_title = ""
        self._update_notes = ""
        self._update_download_url = ""
        self._update_published_at = ""
        
        # High-performance Models
        self._all_anime_model = AnimeModel(self)
        self._day_models = [AnimeModel(self) for _ in range(7)]
        
        # Cache for performance
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        self._ui_model_key = None
        self._data_revision = 0
        
        # Thread pool
        self._thread_pool = QThreadPool()
        logger.info("Multithreading with maximum %d threads", self._thread_pool.maxThreadCount())
        logger.info("Native filter acceleration: %s", "enabled" if is_native_available() else "fallback python")

        # Persistent Settings
        self._settings = QSettings("AiringDeck", "AiringDeck")
        self._use_english_title = self._settings.value("use_english_title", False, type=bool)
        self._selected_genre = self._settings.value("selected_genre", "All genres", type=str)
        self._only_today = self._settings.value("only_today", False, type=bool)
        self._min_score = self._settings.value("min_score", 0, type=int)
        self._sort_field = self._settings.value("sort_field", "airing_time", type=str)
        self._sort_ascending = self._settings.value("sort_ascending", True, type=bool)
        self._app_language = self._settings.value("app_language", "it", type=str)
        if self._app_language not in {"it", "en"}:
            self._app_language = "it"
        self._notifications_enabled = self._settings.value("notifications_enabled", True, type=bool)
        self._notification_lead_minutes = self._settings.value("notification_lead_minutes", 15, type=int)
        if self._notification_lead_minutes not in {5, 15, 30, 60}:
            self._notification_lead_minutes = 15
        self._dismissed_update_version = self._settings.value("dismissed_update_version", "", type=str)
        
        # Calendar State
        self._daily_counts = [0] * 7
        self._full_anime_list = [] # Store original non-filtered list
        
        # Countdown Timer (Update every minute)
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(60000) # 60 seconds
        self._update_timer.timeout.connect(self._on_minute_tick)
        self._update_timer.start()

        # Debounced filter updates to reduce model churn while typing.
        self._filter_update_timer = QTimer(self)
        self._filter_update_timer.setSingleShot(True)
        self._filter_update_timer.setInterval(260)
        self._filter_update_timer.timeout.connect(self._apply_pending_filter)
        
        # Initialize services
        self._auth_service = AuthService()
        self._anilist_service = AniListService()
        self._update_service = UpdateService()
        
        # Connect signals
        self._auth_service.auth_completed.connect(self._on_auth_completed)
        self._auth_service.auth_failed.connect(self._on_auth_failed)
        self._init_tray_icon()
        
        # Lazy initialization via explicit call
        # No heavy work in __init__

    @Slot()
    def initialize(self):
        """Heavy initialization triggered after UI is visible"""
        logger.info("Starting lazy initialization...")
        self.checkForUpdates()
        
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
            self._set_loading(False, self._msg_ready())

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
        loading_changed = self._is_loading != loading
        message_changed = self._status_message != message
        if not loading_changed and not message_changed:
            return
        self._is_loading = loading
        self._status_message = message
        if loading_changed:
            self.isLoadingChanged.emit()
        if message_changed:
            self.statusMessageChanged.emit()

    def _on_auth_completed(self, token: str):
        """Handle successful authentication"""
        logger.info("Auth completed")
        self._anilist_service.set_token(token)
        self._fetch_user_info()
    
    def _on_auth_failed(self, error: str):
        """Handle authentication failure"""
        logger.warning("Auth failed: %s", error)
        self._set_loading(False, self._msg_login_failed(error))
        
    def _fetch_user_info(self):
        """Fetch user info from AniList (Async)"""
        self._set_loading(True, self._msg_fetching_profile())
        
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
            self._set_loading(False, self._msg_logged_in(user["name"]))
            logger.info("Logged in as %s, avatar=%s", user["name"], avatar_url)
            
            # Fetch watching list
            self.syncAnimeList()
        else:
            self._set_loading(False, self._msg_failed_profile())

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
            message = self._tr(
                "Timeout della richiesta. Controlla la connessione e riprova.",
                "Request timeout. Check connection and retry.",
            )
        elif "connectionerror" in lower or "unable to reach" in lower:
            message = self._tr(
                "Rete non disponibile. Controlla la connessione internet.",
                "Network unavailable. Check internet connection.",
            )
        elif "http429" in lower or "rate limit" in lower:
            message = self._tr(
                "Limite AniList raggiunto. Riprova tra poco.",
                "AniList rate limit reached. Retry in a moment.",
            )
        elif "http401" in lower or "not authenticated" in lower:
            message = self._tr(
                "Sessione scaduta. Effettua nuovamente il login.",
                "Session expired. Please login again.",
            )
        else:
            message = self._tr(
                "Errore imprevisto durante la sincronizzazione.",
                "Unexpected error while syncing data.",
            )

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

    @Property(str, notify=appLanguageChanged)
    def appLanguage(self):
        return self._app_language

    @appLanguage.setter
    def appLanguage(self, value):
        value = (value or "it").lower().strip()
        if value not in {"it", "en"}:
            value = "it"
        if self._app_language == value:
            return
        self._app_language = value
        self._settings.setValue("app_language", value)
        self._update_countdowns()
        self.appLanguageChanged.emit()
        self.statusMessageChanged.emit()

    @Property(bool, notify=notificationsEnabledChanged)
    def notificationsEnabled(self):
        return self._notifications_enabled

    @notificationsEnabled.setter
    def notificationsEnabled(self, value):
        value = bool(value)
        if self._notifications_enabled == value:
            return
        self._notifications_enabled = value
        self._settings.setValue("notifications_enabled", value)
        if not value:
            self._last_notification_media_id = None
        self.notificationsEnabledChanged.emit()
        if value:
            self._check_episode_notifications()

    @Property(int, notify=notificationLeadMinutesChanged)
    def notificationLeadMinutes(self):
        return self._notification_lead_minutes

    @notificationLeadMinutes.setter
    def notificationLeadMinutes(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 15
        if value not in {5, 15, 30, 60}:
            value = 15
        if self._notification_lead_minutes == value:
            return
        self._notification_lead_minutes = value
        self._settings.setValue("notification_lead_minutes", value)
        self.notificationLeadMinutesChanged.emit()
        if self._notifications_enabled:
            self._check_episode_notifications()
    
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
        if value == self._pending_filter_text:
            return
        self._pending_filter_text = value
        self._filter_update_timer.start()

    def _apply_pending_filter(self):
        if self._filter_text == self._pending_filter_text:
            return
        self._filter_text = self._pending_filter_text
        self._update_ui_models()
        self.filterTextChanged.emit()
        self.animeListChanged.emit()

    @Property('QVariantList', notify=availableGenresChanged)
    def availableGenres(self):
        return self._available_genres

    @Property(str, notify=selectedGenreChanged)
    def selectedGenre(self):
        return self._selected_genre

    @selectedGenre.setter
    def selectedGenre(self, value):
        value = value or "All genres"
        if self._selected_genre == value:
            return
        self._selected_genre = value
        self._settings.setValue("selected_genre", value)
        self._update_ui_models()
        self.selectedGenreChanged.emit()
        self.animeListChanged.emit()

    @Property(bool, notify=onlyTodayChanged)
    def onlyToday(self):
        return self._only_today

    @onlyToday.setter
    def onlyToday(self, value):
        value = bool(value)
        if self._only_today == value:
            return
        self._only_today = value
        self._settings.setValue("only_today", value)
        self._update_ui_models()
        self.onlyTodayChanged.emit()
        self.animeListChanged.emit()

    @Property(int, notify=minScoreChanged)
    def minScore(self):
        return self._min_score

    @minScore.setter
    def minScore(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 0
        value = max(0, min(100, value))
        if self._min_score == value:
            return
        self._min_score = value
        self._settings.setValue("min_score", value)
        self._update_ui_models()
        self.minScoreChanged.emit()
        self.animeListChanged.emit()

    @Property(str, notify=sortFieldChanged)
    def sortField(self):
        return self._sort_field

    @sortField.setter
    def sortField(self, value):
        allowed = {"airing_time", "title", "progress", "score"}
        value = value if value in allowed else "airing_time"
        if self._sort_field == value:
            return
        self._sort_field = value
        self._settings.setValue("sort_field", value)
        self._update_ui_models()
        self.sortFieldChanged.emit()
        self.animeListChanged.emit()

    @Property(bool, notify=sortAscendingChanged)
    def sortAscending(self):
        return self._sort_ascending

    @sortAscending.setter
    def sortAscending(self, value):
        value = bool(value)
        if self._sort_ascending == value:
            return
        self._sort_ascending = value
        self._settings.setValue("sort_ascending", value)
        self._update_ui_models()
        self.sortAscendingChanged.emit()
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

    @Property(bool, notify=updateAvailableChanged)
    def updateAvailable(self):
        return self._update_available

    @Property(str, notify=updateInfoChanged)
    def updateLatestVersion(self):
        return self._update_latest_version

    @Property(str, notify=updateInfoChanged)
    def updateTitle(self):
        return self._update_title

    @Property(str, notify=updateInfoChanged)
    def updateNotes(self):
        return self._update_notes

    @Property(str, notify=updateInfoChanged)
    def updateDownloadUrl(self):
        return self._update_download_url

    @Property(str, notify=updateInfoChanged)
    def updatePublishedAt(self):
        return self._update_published_at

    @Slot()
    def checkForUpdates(self):
        if self._update_check_in_progress:
            return
        self._update_check_in_progress = True

        worker = Worker(self._update_service.check_latest, APP_VERSION)
        worker.signals.result.connect(self._on_update_check_result)
        worker.signals.error.connect(self._on_update_check_error)
        worker.signals.finished.connect(self._on_update_check_finished)
        self._thread_pool.start(worker)

    def _on_update_check_result(self, payload):
        if not isinstance(payload, dict):
            return
        latest = str(payload.get("latest_version") or "").strip()
        available = bool(payload.get("available"))

        self._update_latest_version = latest
        self._update_title = str(payload.get("title") or "")
        self._update_notes = str(payload.get("notes") or "")
        self._update_download_url = str(payload.get("download_url") or "")
        self._update_published_at = str(payload.get("published_at") or "")

        if available and latest and latest == self._dismissed_update_version:
            available = False

        if self._update_available != available:
            self._update_available = available
            self.updateAvailableChanged.emit()
        self.updateInfoChanged.emit()

    def _on_update_check_error(self, err):
        err_text = self._extract_error_text(err)
        logger.info("Update check failed or unavailable: %s", err_text)

    def _on_update_check_finished(self):
        self._update_check_in_progress = False

    @Slot()
    def openUpdatePage(self):
        if not self._update_download_url:
            return
        if not QDesktopServices.openUrl(QUrl(self._update_download_url)):
            logger.warning("Failed to open update URL: %s", self._update_download_url)

    @Slot()
    def dismissUpdateNotice(self):
        if self._update_latest_version:
            self._dismissed_update_version = self._update_latest_version
            self._settings.setValue("dismissed_update_version", self._dismissed_update_version)
        if self._update_available:
            self._update_available = False
            self.updateAvailableChanged.emit()
    
    # Slots (callable from QML)
    @Slot()
    def login(self):
        """Trigger AniList OAuth login"""
        logger.info("Login requested")
        self._set_loading(True, self._msg_waiting_browser_login())
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
        self._notified_episode_times.clear()
        self._last_notification_media_id = None
        self._selected_anime = None
        self._daily_counts = [0] * 7
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        # Force a UI refresh even when filter state is unchanged.
        self._data_revision += 1
        self._ui_model_key = None
        if self._available_genres != ["All genres"]:
            self._available_genres = ["All genres"]
            self.availableGenresChanged.emit()
        self._update_ui_models()
        
        self.authenticated.emit(False)
        self.userInfoChanged.emit()
        self.selectedAnimeChanged.emit()
        self.dailyCountsChanged.emit()
        self.animeListChanged.emit()
        self._set_loading(False, self._msg_logged_out())

    @Slot()
    def toggleSortDirection(self):
        self.sortAscending = not self._sort_ascending

    @Slot()
    def resetAllFilters(self):
        changed = False
        if self._filter_text or self._pending_filter_text:
            self._filter_text = ""
            self._pending_filter_text = ""
            self.filterTextChanged.emit()
            changed = True
        if self._selected_genre != "All genres":
            self._selected_genre = "All genres"
            self._settings.setValue("selected_genre", self._selected_genre)
            self.selectedGenreChanged.emit()
            changed = True
        if self._only_today:
            self._only_today = False
            self._settings.setValue("only_today", False)
            self.onlyTodayChanged.emit()
            changed = True
        if self._min_score != 0:
            self._min_score = 0
            self._settings.setValue("min_score", 0)
            self.minScoreChanged.emit()
            changed = True
        if self._sort_field != "airing_time":
            self._sort_field = "airing_time"
            self._settings.setValue("sort_field", self._sort_field)
            self.sortFieldChanged.emit()
            changed = True
        if not self._sort_ascending:
            self._sort_ascending = True
            self._settings.setValue("sort_ascending", True)
            self.sortAscendingChanged.emit()
            changed = True

        if changed:
            self._update_ui_models()
            self.animeListChanged.emit()
    
    @Slot()
    def syncAnimeList(self):
        """Sync anime list from AniList"""
        logger.info("Sync anime list requested")
        if not self._is_authenticated:
            self._set_loading(False, self._msg_login_required_sync())
            return

        user_id = self._user_info.get("id")
        if not user_id:
            self._set_loading(False, self._msg_missing_profile_for_sync())
            return

        if self._sync_in_progress:
            self._sync_queued = True
            self._set_loading(True, self._msg_sync_queued())
            return

        self._start_sync_worker(user_id)

    def _start_sync_worker(self, user_id: int):
        self._sync_in_progress = True
        self._set_loading(True, self._msg_syncing_anime_list())
        worker = Worker(self._anilist_service.get_watching_anime, user_id)
        worker.signals.result.connect(self._on_sync_worker_result)
        worker.signals.error.connect(self._on_sync_worker_error)
        self._thread_pool.start(worker)

    def _on_sync_worker_result(self, anime_list):
        self._sync_in_progress = False
        self._sync_retry_attempts = 0
        self._on_anime_list_result(anime_list)
        self._drain_queued_sync_request()

    def _on_sync_worker_error(self, err):
        self._sync_in_progress = False
        err_text = self._extract_error_text(err)
        lower = err_text.lower()
        user_id = self._user_info.get("id")

        if (
            self._is_transient_sync_error(lower)
            and self._sync_retry_attempts < self._max_sync_retry_attempts
            and self._is_authenticated
            and user_id
        ):
            self._sync_retry_attempts += 1
            logger.warning(
                "Transient sync error, auto-retrying (%d/%d): %s",
                self._sync_retry_attempts,
                self._max_sync_retry_attempts,
                err_text,
            )
            self._set_loading(
                True,
                self._msg_retrying_sync(self._sync_retry_attempts, self._max_sync_retry_attempts),
            )
            self._start_sync_worker(int(user_id))
            return

        self._sync_retry_attempts = 0
        self._on_error(err)
        self._drain_queued_sync_request()

    def _drain_queued_sync_request(self):
        if not self._sync_queued:
            return
        self._sync_queued = False
        if self._sync_in_progress or not self._is_authenticated:
            return
        user_id = self._user_info.get("id")
        if not user_id:
            return
        self._start_sync_worker(int(user_id))

    def _is_transient_sync_error(self, lower_error: str) -> bool:
        return (
            "timeout" in lower_error
            or "connectionerror" in lower_error
            or "unable to reach" in lower_error
            or "http429" in lower_error
            or "rate limit" in lower_error
            or "http5" in lower_error
            or "requesterror" in lower_error
            or "invalidresponse" in lower_error
        )
    
    @Slot(int)
    def selectAnime(self, anime_id: int):
        """Select an anime to show details"""
        logger.debug("Selecting anime ID: %d", anime_id)
        selected = self._anime_by_id.get(anime_id)
        if selected is None:
            return
        current = self._selected_anime
        current_id = (current or {}).get("media", {}).get("id")
        new_id = selected.get("media", {}).get("id")
        if current_id == new_id and current is selected:
            return
        self._selected_anime = selected
        self.selectedAnimeChanged.emit()

    def _get_display_title(self, media):
        """Standardized title selection based on settings"""
        titles = media.get('title', {})
        if self._use_english_title:
            return titles.get('english') or titles.get('romaji') or self._tr("Titolo sconosciuto", "Unknown Title")
        return titles.get('romaji') or titles.get('english') or self._tr("Titolo sconosciuto", "Unknown Title")

    def _format_countdown(self, airing_at):
        """Format countdown with support for days, hours, minutes"""
        now = datetime.now()
        dt = datetime.fromtimestamp(airing_at)
        diff = dt - now
        
        time_str = dt.strftime("%H:%M")
        seconds = diff.total_seconds()
        
        if seconds <= -3600: # Over an hour ago
            return self._tr(f"Già uscito alle {time_str}", f"Aired at {time_str}")
        elif seconds <= 0: # Within the last hour
            return self._tr("In onda ora", "Airing now")
        
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
            self._data_revision += 1
            self._ui_model_key = None
            self._update_ui_models()
            self.animeListChanged.emit()

    def _on_minute_tick(self):
        self._update_countdowns()
        self._check_episode_notifications()

    def _update_ui_models(self):
        """Sync Python data to QML models with filtering"""
        query = self._filter_text.lower().strip()
        selected_genre = self._selected_genre.lower().strip()
        today_weekday = datetime.now().weekday()
        model_key = (
            self._data_revision,
            query,
            selected_genre,
            self._only_today,
            self._min_score,
            self._sort_field,
            self._sort_ascending,
            today_weekday,
        )
        if model_key == self._ui_model_key:
            return
        self._ui_model_key = model_key

        filtered_counts = [0] * 7
        # Update Individual Day Models
        for i in range(7):
            day_list = self._weekly_schedule_cache[i]
            if self._only_today and i != today_weekday:
                filtered_day = []
            else:
                filtered_day = self._apply_filters(day_list, query, selected_genre)
                filtered_day = self._sort_entries(filtered_day)
            self._day_models[i].update_data(filtered_day)
            filtered_counts[i] = len(filtered_day)

        # Update Full Model (Airing Only)
        full_airing = self._full_airing_entries
        if self._only_today:
            full_airing = [e for e in full_airing if e.get("calendar_day") == today_weekday]
        full_airing = self._apply_filters(full_airing, query, selected_genre)
        full_airing = self._sort_entries(full_airing)
        self._all_anime_model.update_data(full_airing)
        if filtered_counts != self._daily_counts:
            self._daily_counts = filtered_counts
            self.dailyCountsChanged.emit()

    def _apply_filters(self, entries, query: str, selected_genre: str):
        return filter_entries_advanced(
            entries,
            query,
            selected_genre,
            self._min_score,
            self._only_today,
            datetime.now().weekday(),
        )

    def _sort_entries(self, entries):
        if len(entries) < 2:
            return entries

        reverse = not self._sort_ascending

        if self._sort_field == "title":
            return sorted(entries, key=lambda e: (e.get("display_title") or "").lower(), reverse=reverse)
        if self._sort_field == "progress":
            return sorted(entries, key=lambda e: int(e.get("progress") or 0), reverse=reverse)
        if self._sort_field == "score":
            return sorted(
                entries,
                key=lambda e: int(e.get("media", {}).get("averageScore") or -1),
                reverse=reverse,
            )

        # Default: airing_time
        def airing_key(entry):
            nxt = entry.get("media", {}).get("nextAiringEpisode")
            airing_at = nxt.get("airingAt") if nxt else None
            return airing_at if airing_at is not None else 10**18

        return sorted(entries, key=airing_key, reverse=reverse)

    def _on_anime_list_result(self, anime_list, from_cache=False):
        """Handle anime list result and process for calendar"""
        self._full_anime_list = anime_list
        self._data_revision += 1
        self._ui_model_key = None
        self._anime_by_id = {}
        self._daily_counts = [0] * 7
        self._weekly_schedule_cache = [[] for _ in range(7)]
        self._full_airing_entries = []
        genre_set = set()
        
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
                entry['airing_time_formatted'] = self._tr("Da annunciare", "TBA")
                entry['is_today'] = False

            for genre in media.get("genres", []):
                if genre:
                    genre_set.add(genre)

        if not from_cache:
            self._save_offline_cache()

        new_genres = ["All genres"] + sorted(genre_set)
        if new_genres != self._available_genres:
            self._available_genres = new_genres
            if self._selected_genre not in self._available_genres:
                self._selected_genre = "All genres"
                self._settings.setValue("selected_genre", self._selected_genre)
                self.selectedGenreChanged.emit()
            self.availableGenresChanged.emit()

        self._update_ui_models()
        self.animeListChanged.emit()
        self._check_episode_notifications()
        self._set_loading(False, self._msg_synced_count(len(anime_list)))
        logger.info("Synced %d anime. Day counts: %s", len(anime_list), self._daily_counts)

    def _init_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.info("System tray not available: desktop notifications disabled")
            return
        app = QApplication.instance()
        if app is None:
            return
        self._tray_icon = QSystemTrayIcon(self)
        icon = app.windowIcon()
        if icon and not icon.isNull():
            self._tray_icon.setIcon(icon)
        self._tray_icon.messageClicked.connect(self._on_tray_message_clicked)
        self._tray_icon.show()

    def _on_tray_message_clicked(self):
        media_id = self._last_notification_media_id
        if media_id is None:
            return
        self.selectAnime(int(media_id))

    @Slot()
    def sendTestNotification(self):
        """Emit a manual test notification for diagnostics."""
        if self._tray_icon is None:
            logger.info("Test notification skipped: system tray unavailable")
            return
        summary = self._tr("Notifica di prova", "Test notification")
        body = self._tr(
            "Questa è una notifica di test di AiringDeck.",
            "This is an AiringDeck test notification.",
        )
        self._tray_icon.showMessage(summary, body, QSystemTrayIcon.Information, 8000)
        logger.info("Test notification dispatched")

    def _prune_notified_episode_cache(self, now_ts: int):
        threshold = now_ts - 7200
        self._notified_episode_times = {
            key: airing_at
            for key, airing_at in self._notified_episode_times.items()
            if airing_at >= threshold
        }

    def _check_episode_notifications(self):
        if not self._notifications_enabled:
            return
        if self._tray_icon is None:
            return
        if not self._full_airing_entries:
            return

        now_ts = int(datetime.now().timestamp())
        self._prune_notified_episode_cache(now_ts)
        lead_seconds = max(60, int(self._notification_lead_minutes) * 60)

        for entry in self._full_airing_entries:
            media = entry.get("media", {})
            airing = media.get("nextAiringEpisode")
            if not airing:
                continue
            airing_at = int(airing.get("airingAt") or 0)
            if airing_at <= now_ts:
                continue
            delta = airing_at - now_ts
            if delta > lead_seconds:
                continue

            media_id = media.get("id")
            episode = int(airing.get("episode") or 0)
            if media_id is None or episode <= 0:
                continue

            key = f"{media_id}:{episode}:{airing_at}"
            if key in self._notified_episode_times:
                continue

            title = entry.get("display_title") or self._tr("Titolo sconosciuto", "Unknown Title")
            time_str = datetime.fromtimestamp(airing_at).strftime("%H:%M")
            summary = self._tr("Prossimo episodio", "Upcoming episode")
            body = self._tr(
                f"{title}\nEp {episode} alle {time_str}",
                f"{title}\nEp {episode} at {time_str}",
            )
            self._tray_icon.showMessage(summary, body, QSystemTrayIcon.Information, 10000)
            self._notified_episode_times[key] = airing_at
            self._last_notification_media_id = int(media_id)

    def _tr(self, it_text: str, en_text: str) -> str:
        return en_text if self._app_language == "en" else it_text

    def _msg_ready(self) -> str:
        return self._tr("Pronto", "Ready")

    def _msg_login_failed(self, error: str) -> str:
        return self._tr(f"Login fallito: {error}", f"Login failed: {error}")

    def _msg_fetching_profile(self) -> str:
        return self._tr("Recupero profilo utente...", "Fetching user profile...")

    def _msg_logged_in(self, username: str) -> str:
        return self._tr(f"Accesso eseguito come {username}", f"Logged in as {username}")

    def _msg_failed_profile(self) -> str:
        return self._tr("Impossibile caricare il profilo", "Failed to load profile")

    def _msg_waiting_browser_login(self) -> str:
        return self._tr("In attesa del login dal browser...", "Waiting for browser login...")

    def _msg_logged_out(self) -> str:
        return self._tr("Disconnesso", "Logged out")

    def _msg_syncing_anime_list(self) -> str:
        return self._tr("Sincronizzazione lista anime...", "Syncing anime list...")

    def _msg_sync_queued(self) -> str:
        return self._tr(
            "Sincronizzazione già in corso, nuova richiesta in coda...",
            "Sync already running, queued a new request...",
        )

    def _msg_retrying_sync(self, attempt: int, max_attempts: int) -> str:
        return self._tr(
            f"Rete instabile, nuovo tentativo {attempt}/{max_attempts}...",
            f"Unstable network, retrying {attempt}/{max_attempts}...",
        )

    def _msg_login_required_sync(self) -> str:
        return self._tr(
            "Effettua il login per sincronizzare la lista.",
            "Login is required to sync the list.",
        )

    def _msg_missing_profile_for_sync(self) -> str:
        return self._tr(
            "Profilo non pronto, riprova tra poco.",
            "Profile not ready yet, try again shortly.",
        )

    def _msg_synced_count(self, count: int) -> str:
        return self._tr(f"Sincronizzati {count} anime", f"Synced {count} anime")
