import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

import "components"
import "components/Calendar"

FocusScope {
    id: mainContent
    property bool isEnglishUi: appController.appLanguage === "en"
    readonly property int sidebarMainDecodeWidth: 800
    readonly property int sidebarMainDecodeHeight: 450
    property string sidebarCoverSource: ""
    property string pendingSidebarCoverSource: ""
    property var weekdays: mainContent.isEnglishUi
        ? ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        : ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    property var sortOptions: [
        { label: mainContent.tr("Ordina: Uscita", "Sort: Airing"), value: "airing_time" },
        { label: mainContent.tr("Ordina: Titolo", "Sort: Title"), value: "title" },
        { label: mainContent.tr("Ordina: Progresso", "Sort: Progress"), value: "progress" },
        { label: mainContent.tr("Ordina: Voto", "Sort: Score"), value: "score" }
    ]

    function tr(itText, enText) {
        return mainContent.isEnglishUi ? enText : itText
    }
    
    function resolveSidebarCover(selectedAnime) {
        if (!selectedAnime || !selectedAnime.media || !selectedAnime.media.coverImage) {
            return ""
        }
        var cover = selectedAnime.media.coverImage
        return cover.extraLarge || cover.large || cover.medium || ""
    }

    function refreshSidebarCoverSource() {
        var nextSource = mainContent.resolveSidebarCover(appController.selectedAnime)
        if (nextSource === "") {
            sidebarCoverUpdateTimer.stop()
            pendingSidebarCoverSource = ""
            if (sidebarCoverSource !== "") {
                sidebarCoverSource = ""
            }
            return
        }
        if (nextSource === sidebarCoverSource && nextSource === pendingSidebarCoverSource) {
            return
        }
        pendingSidebarCoverSource = nextSource
        sidebarCoverUpdateTimer.restart()
    }

    function genreIndexOf(value) {
        for (var i = 0; i < appController.availableGenres.length; i++) {
            if (appController.availableGenres[i] === value) {
                return i
            }
        }
        return 0
    }

    function genreLabel(value) {
        if (!value || value === "All genres") {
            return mainContent.tr("Tutti i generi", "All genres")
        }
        if (mainContent.isEnglishUi) {
            return value
        }
        var map = {
            "Action": "Azione",
            "Adventure": "Avventura",
            "Comedy": "Commedia",
            "Drama": "Drammatico",
            "Ecchi": "Ecchi",
            "Fantasy": "Fantasy",
            "Hentai": "Hentai",
            "Horror": "Horror",
            "Mahou Shoujo": "Magical Girl",
            "Mecha": "Mecha",
            "Music": "Musica",
            "Mystery": "Mistero",
            "Psychological": "Psicologico",
            "Romance": "Romantico",
            "Sci-Fi": "Fantascienza",
            "Slice of Life": "Slice of Life",
            "Sports": "Sport",
            "Supernatural": "Soprannaturale",
            "Thriller": "Thriller"
        }
        return map[value] || value
    }

    function formattedUpdateNotes() {
        if (!appController.updateNotes || appController.updateNotes.length === 0) {
            return mainContent.tr(
                "Nuova versione disponibile. Consulta la pagina release per i dettagli.",
                "A new version is available. Open the release page for details."
            )
        }
        return appController.updateNotes
    }
    
    // Parent handles window properties
    
    Item {
        id: uiScene
        anchors.fill: parent

        // Main layout with background gradient
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#1f2937" }
                GradientStop { position: 1.0; color: "#111827" }
            }
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0
        
        // Calendar area (60%)
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.6
            color: "#111827"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                
                // Header
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    color: "#1f2937"
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 20
                        
                        // Logo + Title
                        RowLayout {
                            spacing: 12
                            
                            Logo {
                                width: 42
                                height: 42
                                primaryColor: "#34d399"
                                animated: true
                            }
                            
                            Text {
                                text: "AiringDeck"
                                font.pixelSize: 24
                                font.bold: true
                                color: "#ffffff"
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: aboutDialog.open()
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        // Search bar
                        Rectangle {
                            Layout.preferredWidth: 350
                            Layout.preferredHeight: 40
                            color: "#374151"
                            radius: 8
                            opacity: 0.8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 10
                                
                                Text {
                                    text: "🔍"
                                    font.pixelSize: 16
                                    color: "#9ca3af"
                                }
                                
                                TextInput {
                                    id: searchInput
                                    Layout.fillWidth: true
                                    color: "#ffffff"
                                    font.pixelSize: 14
                                    enabled: true
                                    verticalAlignment: Text.AlignVCenter
                                    activeFocusOnTab: true
                                    KeyNavigation.tab: genreCombo
                                    Accessible.role: Accessible.EditableText
                                    Accessible.name: mainContent.tr("Cerca anime", "Search anime")
                                    Accessible.description: mainContent.tr(
                                        "Campo di ricerca per filtrare la lista anime",
                                        "Search field to filter the anime list"
                                    )
                                    
                                    onTextChanged: {
                                        appController.setFilterText(text)
                                    }
                                    
                                    Text {
                                        text: mainContent.tr("Cerca anime...", "Search anime...")
                                        color: "#6b7280"
                                        visible: parent.text.length === 0 && !searchInput.activeFocus
                                        font.pixelSize: 14
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                }
                            }
                        }
                        
                        // Sync Button
                        Rectangle {
                            id: syncButton
                            width: 40
                            height: 40
                            radius: 8
                            color: syncMouseArea.containsMouse ? "#4b5563" : "#374151"
                            activeFocusOnTab: true
                            KeyNavigation.tab: profileButton
                            KeyNavigation.backtab: searchInput
                            Accessible.role: Accessible.Button
                            Accessible.name: mainContent.tr("Sincronizza lista", "Synchronize list")
                            Accessible.description: mainContent.tr(
                                "Aggiorna dal server AniList la lista anime",
                                "Refresh anime list from AniList server"
                            )
                            Keys.onReturnPressed: appController.syncAnimeList()
                            Keys.onEnterPressed: appController.syncAnimeList()
                            Keys.onSpacePressed: appController.syncAnimeList()
                            
                            Text {
                                anchors.centerIn: parent
                                text: "🔄"
                                font.pixelSize: 18
                                color: appController.isLoading ? "#3b82f6" : "white"
                                
                                RotationAnimation on rotation {
                                    running: appController.isLoading
                                    from: 0
                                    to: 360
                                    duration: 1000
                                    loops: Animation.Infinite
                                }
                            }
                            
                            MouseArea {
                                id: syncMouseArea
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: appController.syncAnimeList()
                            }
                            
                            ToolTip.visible: syncMouseArea.containsMouse
                            ToolTip.text: mainContent.tr("Sincronizza lista", "Synchronize list")
                            ToolTip.delay: 500
                        }
                        
                        // Login/Profile Section
                        Rectangle {
                            id: profileButton
                            Layout.preferredWidth: appController.isAuthenticated ? 200 : 180
                            Layout.preferredHeight: 40
                            color: appController.isAuthenticated ? "transparent" : "#3b82f6"
                            radius: 8
                            border.color: appController.isAuthenticated ? "#4b5563" : "transparent"
                            border.width: appController.isAuthenticated ? 1 : 0
                            activeFocusOnTab: true
                            KeyNavigation.tab: genreCombo
                            KeyNavigation.backtab: syncButton
                            Accessible.role: Accessible.Button
                            Accessible.name: appController.isAuthenticated
                                             ? mainContent.tr("Menu utente", "User menu")
                                             : mainContent.tr("Login AniList", "AniList login")
                            Accessible.description: appController.isAuthenticated
                                                    ? mainContent.tr(
                                                        "Apri menu impostazioni e logout",
                                                        "Open settings and logout menu"
                                                    )
                                                    : mainContent.tr(
                                                        "Avvia autenticazione AniList",
                                                        "Start AniList authentication"
                                                    )
                            Keys.onReturnPressed: {
                                if (appController.isAuthenticated) {
                                    userMenu.open()
                                } else {
                                    appController.login()
                                }
                            }
                            Keys.onEnterPressed: {
                                if (appController.isAuthenticated) {
                                    userMenu.open()
                                } else {
                                    appController.login()
                                }
                            }
                            Keys.onSpacePressed: {
                                if (appController.isAuthenticated) {
                                    userMenu.open()
                                } else {
                                    appController.login()
                                }
                            }
                            
                            MouseArea {
                                id: profileArea
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (appController.isAuthenticated) {
                                        userMenu.open()
                                    } else {
                                        appController.login()
                                    }
                                }
                            }
                            
                            Menu {
                                id: userMenu
                                y: parent.height
                                
                                MenuItem {
                                    text: mainContent.tr("Impostazioni", "Settings")
                                    onTriggered: settingsDialog.open()
                                }
                                
                                MenuItem {
                                    text: mainContent.tr("Logout", "Logout")
                                    onTriggered: appController.logout()
                                }
                            }
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 10
                                
                                Rectangle {
                                    width: 28
                                    height: 28
                                    radius: 14
                                    color: "#374151"
                                    clip: true
                                    Layout.alignment: Qt.AlignVCenter

                                    Image {
                                        anchors.fill: parent
                                        source: appController.userAvatar
                                        fillMode: Image.PreserveAspectCrop
                                        asynchronous: true
                                    }
                                }
                                
                                Text {
                                    text: appController.isAuthenticated ? (appController.userInfo.name || "User") : ("🔐 " + mainContent.tr("Login", "Login"))
                                    color: "#ffffff"
                                    font.pixelSize: 13
                                    font.bold: !appController.isAuthenticated
                                    Layout.alignment: Qt.AlignVCenter
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                
                                Text {
                                    text: "▼"
                                    color: "#9ca3af"
                                    font.pixelSize: 10
                                    visible: appController.isAuthenticated
                                    Layout.alignment: Qt.AlignVCenter
                                }
                            }
                        }
                    }
                }

                // Filters and sorting row
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 66
                    color: "#0f172a"

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        readonly property bool compactLayout: width < 1120
                        spacing: compactLayout ? 6 : 10

                        ComboBox {
                            id: genreCombo
                            Layout.preferredWidth: parent.compactLayout ? 160 : 190
                            model: appController.availableGenres
                            currentIndex: mainContent.genreIndexOf(appController.selectedGenre)
                            activeFocusOnTab: true
                            KeyNavigation.tab: minScoreSpin
                            KeyNavigation.backtab: profileButton
                            Accessible.name: mainContent.tr("Filtro genere", "Genre filter")
                            Accessible.description: mainContent.tr(
                                "Seleziona il genere da mostrare",
                                "Select genre to display"
                            )
                            displayText: mainContent.genreLabel(
                                (currentIndex >= 0 && currentIndex < model.length) ? model[currentIndex] : "All genres"
                            )
                            contentItem: Text {
                                leftPadding: 10
                                rightPadding: genreCombo.indicator.width + genreCombo.spacing
                                text: genreCombo.displayText
                                color: "#f3f4f6"
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                                font.pixelSize: 13
                            }
                            background: Rectangle {
                                radius: 6
                                color: "#1f2937"
                                border.color: "#4b5563"
                                border.width: 1
                            }
                            delegate: ItemDelegate {
                                width: parent.width
                                highlighted: genreCombo.highlightedIndex === index
                                contentItem: Text {
                                    text: mainContent.genreLabel(modelData)
                                    color: highlighted ? "#ffffff" : "#e5e7eb"
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                }
                                background: Rectangle {
                                    color: highlighted ? "#2563eb" : (parent.hovered ? "#374151" : "#111827")
                                }
                            }
                            onActivated: {
                                if (currentIndex >= 0 && currentIndex < model.length) {
                                    appController.selectedGenre = model[currentIndex]
                                }
                            }
                        }

                        RowLayout {
                            spacing: 6

                            Text {
                                text: parent.parent.compactLayout
                                      ? mainContent.tr("Voto min", "Min score")
                                      : mainContent.tr("Voto minimo", "Min score")
                                color: "#f3f4f6"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.alignment: Qt.AlignVCenter
                            }

                            SpinBox {
                                id: minScoreSpin
                                from: 0
                                to: 100
                                stepSize: 1
                                editable: true
                                value: appController.minScore
                                Layout.preferredWidth: parent.parent.compactLayout ? 104 : 120
                                activeFocusOnTab: true
                                KeyNavigation.tab: onlyTodayCheck
                                KeyNavigation.backtab: genreCombo
                                Accessible.name: mainContent.tr("Voto minimo", "Minimum score")
                                Accessible.description: mainContent.tr(
                                    "Imposta il voto minimo degli anime mostrati",
                                    "Set the minimum score for displayed anime"
                                )
                                onValueModified: appController.minScore = value
                                ToolTip.visible: hovered
                                ToolTip.text: mainContent.tr(
                                                  "Mostra solo anime con voto >= al valore impostato",
                                                  "Show only anime with score >= selected value"
                                              )
                            }
                        }

                        CheckBox {
                            id: onlyTodayCheck
                            checked: appController.onlyToday
                            activeFocusOnTab: true
                            KeyNavigation.tab: sortCombo
                            KeyNavigation.backtab: minScoreSpin
                            Accessible.name: mainContent.tr("Solo episodi oggi", "Only episodes today")
                            Accessible.description: mainContent.tr(
                                "Mostra solo anime con episodio in uscita oggi",
                                "Show only anime with an episode airing today"
                            )
                            onToggled: appController.onlyToday = checked
                            contentItem: Text {
                                text: parent.parent.compactLayout
                                      ? mainContent.tr("Solo oggi", "Only today")
                                      : mainContent.tr("Solo episodi oggi", "Only episodes today")
                                color: "#ffffff"
                                font.pixelSize: 13
                                font.bold: true
                                leftPadding: onlyTodayCheck.indicator.width + onlyTodayCheck.spacing
                                verticalAlignment: Text.AlignVCenter
                            }
                            indicator: Rectangle {
                                implicitWidth: 18
                                implicitHeight: 18
                                radius: 4
                                border.width: 1
                                border.color: onlyTodayCheck.checked ? "#22c55e" : "#9ca3af"
                                color: onlyTodayCheck.checked ? "#16a34a" : "#1f2937"

                                Text {
                                    anchors.centerIn: parent
                                    text: onlyTodayCheck.checked ? "✓" : ""
                                    color: "white"
                                    font.pixelSize: 12
                                    font.bold: true
                                }
                            }
                            ToolTip.visible: hovered
                            ToolTip.text: mainContent.tr(
                                              "Filtra la lista mostrando solo gli anime con episodio in uscita oggi",
                                              "Filter list to anime with an episode airing today"
                                          )
                        }

                        ComboBox {
                            id: sortCombo
                            Layout.preferredWidth: parent.compactLayout ? 150 : 170
                            model: mainContent.sortOptions
                            textRole: "label"
                            activeFocusOnTab: true
                            KeyNavigation.tab: sortDirectionButton
                            KeyNavigation.backtab: onlyTodayCheck
                            Accessible.name: mainContent.tr("Ordinamento", "Sorting")
                            Accessible.description: mainContent.tr(
                                "Seleziona il criterio di ordinamento",
                                "Select sorting criteria"
                            )
                            currentIndex: {
                                for (var i = 0; i < mainContent.sortOptions.length; i++) {
                                    if (mainContent.sortOptions[i].value === appController.sortField) {
                                        return i
                                    }
                                }
                                return 0
                            }
                            contentItem: Text {
                                leftPadding: 10
                                rightPadding: sortCombo.indicator.width + sortCombo.spacing
                                text: sortCombo.displayText
                                color: "#f3f4f6"
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                                font.pixelSize: 13
                            }
                            background: Rectangle {
                                radius: 6
                                color: "#1f2937"
                                border.color: "#4b5563"
                                border.width: 1
                            }
                            delegate: ItemDelegate {
                                width: parent.width
                                highlighted: sortCombo.highlightedIndex === index
                                contentItem: Text {
                                    text: modelData.label
                                    color: highlighted ? "#ffffff" : "#e5e7eb"
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                }
                                background: Rectangle {
                                    color: highlighted ? "#2563eb" : (parent.hovered ? "#374151" : "#111827")
                                }
                            }
                            onActivated: {
                                appController.sortField = mainContent.sortOptions[currentIndex].value
                            }
                        }

                        Button {
                            id: sortDirectionButton
                            text: appController.sortAscending ? "ASC" : "DESC"
                            Layout.preferredWidth: parent.compactLayout ? 74 : 82
                            activeFocusOnTab: true
                            KeyNavigation.tab: resetFiltersButton
                            KeyNavigation.backtab: sortCombo
                            Accessible.name: mainContent.tr(
                                "Direzione ordinamento",
                                "Sort direction"
                            )
                            Accessible.description: mainContent.tr(
                                "Alterna ordinamento crescente o decrescente",
                                "Toggle ascending or descending sort"
                            )
                            onClicked: appController.toggleSortDirection()
                        }

                        Item {
                            visible: !parent.compactLayout
                            Layout.fillWidth: !parent.compactLayout
                        }

                        Button {
                            id: resetFiltersButton
                            text: parent.compactLayout
                                  ? mainContent.tr("Reset", "Reset")
                                  : mainContent.tr("Reset filtri", "Reset filters")
                            Layout.preferredWidth: parent.compactLayout ? 82 : 110
                            activeFocusOnTab: true
                            KeyNavigation.tab: searchInput
                            KeyNavigation.backtab: sortDirectionButton
                            Accessible.name: mainContent.tr("Reset filtri", "Reset filters")
                            Accessible.description: mainContent.tr(
                                "Reimposta ricerca, filtri e ordinamento ai valori predefiniti",
                                "Reset search, filters and sorting to default values"
                            )
                            onClicked: {
                                searchInput.text = ""
                                appController.resetAllFilters()
                            }
                        }
                    }
                }
                
                // Weekly Calendar View (Scrollable)
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: 30
                        anchors.margins: 25
                        
                        Repeater {
                            model: mainContent.weekdays
                            
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 15
                                
                                // Day Header
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 12
                                    
                                    Rectangle {
                                        width: 4
                                        height: 24
                                        color: (index === (new Date().getDay() + 6) % 7) ? "#3b82f6" : "#4b5563"
                                        radius: 2
                                    }
                                    
                                    Text {
                                        text: modelData
                                        color: "#ffffff"
                                        font.pixelSize: 22
                                        font.bold: true
                                    }
                                    
                                    // Today Tag
                                    Rectangle {
                                        visible: index === (new Date().getDay() + 6) % 7
                                        color: "#3b82f6"
                                        Layout.preferredWidth: 45
                                        Layout.preferredHeight: 18
                                        radius: 4
                                        Text {
                                            anchors.centerIn: parent
                                            text: mainContent.tr("OGGI", "TODAY")
                                            color: "white"
                                            font.pixelSize: 10
                                            font.bold: true
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: 32
                                        height: 24
                                        radius: 12
                                        color: "#374151"
                                        Text {
                                            anchors.centerIn: parent
                                            text: appController.dailyCounts[index]
                                            color: "#9ca3af"
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }
                                    
                                    Item { Layout.fillWidth: true }
                                }
                                
                                // Anime Cards for this day
                                Flow {
                                    Layout.fillWidth: true
                                    spacing: 15
                                    
                                    Repeater {
                                        model: appController.dayModels[index]
                                        delegate: AnimeCard {
                                            // animeData is handled inside AnimeCard via model.media
                                        }
                                    }
                                    
                                    // Empty state for the day
                                    Text {
                                        text: mainContent.tr("Nessuna uscita programmata", "No scheduled releases")
                                        color: "#4b5563"
                                        font.italic: true
                                        font.pixelSize: 14
                                        visible: appController.dayModels[index].count === 0
                                    }
                                }
                                
                                // Divider
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 1
                                    color: "#374151"
                                    opacity: 0.3
                                    visible: index < 6
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                    }
                }
            }
        }
        
        // Sidebar (40%)
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.4
            color: "#1f2937"
            border.color: "#374151"
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                // Anime Details
                ScrollView {
                    id: detailsScroll
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: !!appController.selectedAnime.media
                    clip: true
                    
                    ColumnLayout {
                        // Keep a safety gutter so long text never touches/clips at the viewport edge.
                        width: Math.max(detailsScroll.availableWidth - 12, 0)
                        spacing: 20
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 400
                            radius: 12
                            color: "#111827"
                            clip: true
                            
                            // Focused Foreground Image
                            Image {
                                id: sidebarMainImage
                                anchors.fill: parent
                                source: mainContent.sidebarCoverSource
                                fillMode: Image.PreserveAspectFit
                                asynchronous: true
                                smooth: true
                                cache: false
                                sourceSize.width: mainContent.sidebarMainDecodeWidth
                                sourceSize.height: mainContent.sidebarMainDecodeHeight
                                
                                OpacityAnimator on opacity {
                                    from: 0; to: 1; duration: 400
                                    running: sidebarMainImage.status === Image.Ready
                                }
                            }

                            Rectangle {
                                anchors.fill: parent
                                color: "#0b1220"
                                opacity: 0.12
                                visible: sidebarMainImage.status === Image.Ready
                            }

                            Text {
                                anchors.centerIn: parent
                                visible: sidebarMainImage.source === "" || sidebarMainImage.status === Image.Error
                                text: mainContent.tr("Cover non disponibile", "Cover unavailable")
                                color: "#6b7280"
                                font.pixelSize: 14
                            }
                        }
                            // Title
                            Text {
                                Layout.fillWidth: true
                                Layout.rightMargin: 8
                                text: appController.selectedAnime.display_title || ""
                                color: "#ffffff"
                                font.pixelSize: 22
                                minimumPixelSize: 16
                                fontSizeMode: Text.Fit
                                font.bold: true
                                wrapMode: Text.WordWrap
                                maximumLineCount: 4
                                elide: Text.ElideRight
                            }
                            
                            // Countdown / Airing Info
                            Text {
                                Layout.fillWidth: true
                                visible: !!appController.selectedAnime.media && !!appController.selectedAnime.media.nextAiringEpisode
                                text: mainContent.tr("Prossimo Episodio: ", "Next Episode: ") + appController.selectedAnime.airing_time_formatted
                                color: "#34d399"
                                font.pixelSize: 14
                                font.bold: true
                            }

                            Text {
                                Layout.fillWidth: true
                                text: mainContent.tr("Voto: ", "Score: ") + (appController.selectedAnime.rating_display || "--")
                                color: "#f59e0b"
                                font.pixelSize: 13
                                font.bold: true
                            }

                            Button {
                                Layout.alignment: Qt.AlignLeft
                                Layout.preferredHeight: 38
                                text: mainContent.tr("Open on AniList", "Open on AniList")
                                visible: !!(appController.selectedAnime.media && appController.selectedAnime.media.siteUrl)
                                activeFocusOnTab: true
                                Accessible.role: Accessible.Button
                                Accessible.name: mainContent.tr("Apri su AniList", "Open on AniList")
                                Accessible.description: mainContent.tr(
                                                            "Apre la pagina AniList dell'anime selezionato",
                                                            "Opens the AniList page for the selected anime"
                                                        )
                                onClicked: appController.openSelectedAnimeOnAniList()
                                background: Rectangle {
                                    color: parent.hovered ? "#1f7ae0" : "#2563eb"
                                    radius: 8
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                         
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 60
                            color: "#374151"
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                spacing: 15
                                
                                ColumnLayout {
                                    spacing: 2
                                    Text { text: mainContent.tr("Progresso", "Progress"); color: "#9ca3af"; font.pixelSize: 11 }
                                    Text { 
                                        text: mainContent.tr("Episodio ", "Episode ") + (appController.selectedAnime.progress || 0)
                                        color: "#ffffff"; font.bold: true; font.pixelSize: 14 
                                    }
                                }
                                
                                Rectangle { width: 1; Layout.fillHeight: true; color: "#4b5563" }
                                
                                ColumnLayout {
                                    spacing: 2
                                    Text { text: mainContent.tr("Prossimo", "Next"); color: "#9ca3af"; font.pixelSize: 11 }
                                    Text { 
                                        text: appController.selectedAnime.media && appController.selectedAnime.media.nextAiringEpisode ? 
                                              "Ep " + appController.selectedAnime.media.nextAiringEpisode.episode : "TBA"
                                        color: "#10b981"; font.bold: true; font.pixelSize: 14 
                                    }
                                }
                            }
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: appController.selectedAnime.media ? appController.selectedAnime.media.genres.join(" • ") : ""
                            color: "#3b82f6"
                            font.pixelSize: 12
                            font.bold: true
                            wrapMode: Text.WordWrap
                        }
                    }
                }
                
                // Placeholder when no anime selected
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#111827"
                    radius: 12
                    visible: !appController.selectedAnime.media
                    
                    Column {
                        anchors.centerIn: parent
                        spacing: 10
                        Text {
                            text: "📺 " + mainContent.tr("Seleziona un anime", "Select an anime")
                            color: "#6b7280"
                            font.pixelSize: 18
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: mainContent.tr("per vedere i dettagli", "to view details")
                            color: "#4b5563"
                            font.pixelSize: 14
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
        }
    }
    
        // Status bar at bottom
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 30
            color: "#111827"
            border.color: "#374151"
            border.width: 1
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 10
            
            Text {
                text: appController.isAuthenticated
                      ? ("✅ " + mainContent.tr("Collegato", "Connected"))
                      : ("⚠️ " + mainContent.tr("Offline", "Offline"))
                color: appController.isAuthenticated ? "#10b981" : "#f59e0b"
                font.pixelSize: 12
            }
            
            Rectangle { width: 1; height: 12; color: "#374151" }
            
            Text {
                text: appController.isLoading ? ("⌛ " + appController.statusMessage) : appController.statusMessage
                color: "#9ca3af"
                font.pixelSize: 12
            }
            
            Item { Layout.fillWidth: true }
            
            Text {
                text: "v" + appController.appVersion + " | Qt " + appController.qtVersion
                color: "#6b7280"
                font.pixelSize: 11
            }
        }
        }
    }

    Item {
        id: privacyModalOverlay
        anchors.fill: parent
        z: 12500
        visible: appController.showPrivacyNotice
        focus: visible
        onVisibleChanged: {
            if (visible) {
                continuePrivacyButton.forceActiveFocus()
                privacyNotificationsSwitch.checked = appController.notificationsEnabled
                privacyUpdateChecksSwitch.checked = appController.updateChecksEnabled
                privacyDiagnosticsSwitch.checked = appController.diagnosticsEnabled
            }
        }

        ShaderEffectSource {
            id: privacyOverlaySource
            anchors.fill: uiScene
            sourceItem: uiScene
            live: true
            hideSource: privacyModalOverlay.visible
            visible: privacyModalOverlay.visible
            smooth: true
        }

        MultiEffect {
            anchors.fill: parent
            source: privacyOverlaySource
            blurEnabled: true
            blurMax: 54
            blur: 0.82
            saturation: 0.92
        }

        Rectangle {
            anchors.fill: parent
            color: "#7f020617"
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
        }

        Rectangle {
            id: privacyDialog
            width: Math.min(parent.width - 56, 760)
            height: Math.min(parent.height - 56, privacyDialogContent.implicitHeight + 36)
            anchors.centerIn: parent
            radius: 14
            color: "#0f172a"
            border.color: "#14b8a6"
            border.width: 1
            clip: true

            ScrollView {
                anchors.fill: parent
                anchors.margins: 18
                clip: true
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                ColumnLayout {
                    id: privacyDialogContent
                    width: Math.max(parent.availableWidth - 2, 0)
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: mainContent.tr("Data & Privacy setup", "Data & Privacy setup")
                        color: "#ccfbf1"
                        font.pixelSize: 22
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: mainContent.tr(
                                  "AiringDeck opera in modalita no-tracker: i dati restano locali e non esiste un cloud AiringDeck. Scegli ora come gestire funzioni opzionali.",
                                  "AiringDeck runs in no-tracker mode: data stays local and there is no AiringDeck cloud backend. Choose how optional features should work."
                              )
                        color: "#e2e8f0"
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: privacyOptionsColumn.implicitHeight + 28
                        color: "#111827"
                        radius: 10
                        border.color: "#1f2937"
                        border.width: 1

                        ColumnLayout {
                            id: privacyOptionsColumn
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    Layout.fillWidth: true
                                    text: mainContent.tr("Notifiche episodi", "Episode notifications")
                                    color: "#f8fafc"
                                    font.pixelSize: 14
                                    font.bold: true
                                }
                                Switch {
                                    id: privacyNotificationsSwitch
                                    checked: appController.notificationsEnabled
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    Layout.fillWidth: true
                                    text: mainContent.tr("Controllo aggiornamenti GitHub", "GitHub update checks")
                                    color: "#f8fafc"
                                    font.pixelSize: 14
                                    font.bold: true
                                }
                                Switch {
                                    id: privacyUpdateChecksSwitch
                                    checked: appController.updateChecksEnabled
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Text {
                                    Layout.fillWidth: true
                                    text: mainContent.tr("Diagnostica locale", "Local diagnostics")
                                    color: "#f8fafc"
                                    font.pixelSize: 14
                                    font.bold: true
                                }
                                Switch {
                                    id: privacyDiagnosticsSwitch
                                    checked: appController.diagnosticsEnabled
                                }
                            }
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: mainContent.tr(
                                  "Puoi modificare queste opzioni in qualsiasi momento da Impostazioni.",
                                  "You can change these options anytime from Settings."
                              )
                        color: "#93c5fd"
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Button {
                            text: mainContent.tr("Usa valori correnti", "Use current values")
                            onClicked: appController.acceptPrivacyDefaults()
                            background: Rectangle {
                                color: parent.hovered ? "#334155" : "#1f2937"
                                radius: 8
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#e2e8f0"
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Button {
                            id: continuePrivacyButton
                            text: mainContent.tr("Salva e continua", "Save and continue")
                            activeFocusOnTab: true
                            Accessible.role: Accessible.Button
                            Accessible.name: mainContent.tr("Salva preferenze privacy", "Save privacy preferences")
                            Accessible.description: mainContent.tr(
                                                        "Salva le preferenze e avvia i servizi opzionali",
                                                        "Save preferences and start optional services"
                                                    )
                            onClicked: appController.applyPrivacyPreferences(
                                           privacyNotificationsSwitch.checked,
                                           privacyUpdateChecksSwitch.checked,
                                           privacyDiagnosticsSwitch.checked
                                       )
                            background: Rectangle {
                                color: continuePrivacyButton.hovered ? "#0d9488" : "#0f766e"
                                radius: 8
                            }
                            contentItem: Text {
                                text: continuePrivacyButton.text
                                color: "white"
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }
        }
    }

    Item {
        id: updateModalOverlay
        anchors.fill: parent
        z: 12000
        visible: appController.updateAvailable
        focus: visible
        onVisibleChanged: {
            if (visible) {
                closeUpdateDialogButton.forceActiveFocus()
            }
        }

        ShaderEffectSource {
            id: updateOverlaySource
            anchors.fill: uiScene
            sourceItem: uiScene
            live: true
            hideSource: updateModalOverlay.visible
            visible: updateModalOverlay.visible
            smooth: true
        }

        MultiEffect {
            anchors.fill: parent
            source: updateOverlaySource
            blurEnabled: true
            blurMax: 48
            blur: 0.75
            saturation: 0.95
        }

        Rectangle {
            anchors.fill: parent
            color: "#66000000"
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            cursorShape: Qt.ArrowCursor
        }

        Rectangle {
            id: updateDialog
            width: Math.min(parent.width - 48, 720)
            height: updateDialogContent.implicitHeight + 34
            anchors.centerIn: parent
            radius: 14
            color: "#0f172a"
            border.color: "#3b82f6"
            border.width: 1
            clip: true
            Accessible.role: Accessible.Dialog
            Accessible.name: mainContent.tr("Aggiornamento disponibile", "Update available")

            ColumnLayout {
                id: updateDialogContent
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Text {
                        Layout.fillWidth: true
                        text: mainContent.tr("Aggiornamento disponibile", "Update available")
                        color: "#dbeafe"
                        font.pixelSize: updateDialog.width < 420 ? 16 : 18
                        font.bold: true
                    }

                    ToolButton {
                        id: closeUpdateDialogButton
                        text: "➜"
                        font.pixelSize: 17
                        activeFocusOnTab: true
                        KeyNavigation.tab: updateNowButton
                        KeyNavigation.backtab: updateNowButton
                        Accessible.role: Accessible.Button
                        Accessible.name: mainContent.tr("Chiudi avviso aggiornamento", "Close update notice")
                        Accessible.description: mainContent.tr(
                                                    "Chiude l'avviso senza aggiornare",
                                                    "Dismisses the notice without updating"
                                                )
                        onClicked: appController.dismissUpdateNotice()
                        ToolTip.visible: hovered
                        ToolTip.text: mainContent.tr("Chiudi avviso", "Close notice")
                        background: Rectangle {
                            radius: 6
                            color: closeUpdateDialogButton.hovered ? "#1f2937" : "transparent"
                        }
                        contentItem: Text {
                            text: closeUpdateDialogButton.text
                            color: "#9ca3af"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: closeUpdateDialogButton.font.pixelSize
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: mainContent.tr("Versione attuale: ", "Current version: ")
                          + "v" + appController.appVersion
                          + "  →  "
                          + mainContent.tr("Nuova versione: ", "New version: ")
                          + "v" + appController.updateLatestVersion
                    color: "#93c5fd"
                    font.pixelSize: updateDialog.width < 420 ? 12 : 14
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: mainContent.formattedUpdateNotes()
                    color: "#e5e7eb"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    maximumLineCount: 10
                    elide: Text.ElideRight
                }

                Item { Layout.fillWidth: true; Layout.preferredHeight: 2 }

                Button {
                    id: updateNowButton
                    text: mainContent.tr("Aggiorna ora", "Update now")
                    Layout.alignment: Qt.AlignRight
                    activeFocusOnTab: true
                    KeyNavigation.tab: closeUpdateDialogButton
                    KeyNavigation.backtab: closeUpdateDialogButton
                    Accessible.role: Accessible.Button
                    Accessible.name: mainContent.tr("Aggiorna ora", "Update now")
                    Accessible.description: mainContent.tr(
                                                "Apre la pagina di download dell'aggiornamento",
                                                "Opens the update download page"
                                            )
                    onClicked: appController.openUpdatePage()
                    background: Rectangle {
                        color: updateNowButton.hovered ? "#2563eb" : "#1d4ed8"
                        radius: 8
                    }
                    contentItem: Text {
                        text: updateNowButton.text
                        color: "white"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }

        Keys.onEscapePressed: appController.dismissUpdateNotice()
    }
    
    // Splash Screen is now handled by BootShell
    Timer {
        id: sidebarCoverUpdateTimer
        interval: 48
        repeat: false
        onTriggered: {
            if (mainContent.sidebarCoverSource !== mainContent.pendingSidebarCoverSource) {
                mainContent.sidebarCoverSource = mainContent.pendingSidebarCoverSource
            }
        }
    }

    Connections {
        target: appController
        function onSelectedAnimeChanged() {
            mainContent.refreshSidebarCoverSource()
        }
    }

    Component.onCompleted: mainContent.refreshSidebarCoverSource()

    // Settings Dialog
    Loader {
        id: settingsLoader
        active: true
        source: "components/Settings/SettingsDialog.qml"
    }
    
    property alias settingsDialog: settingsLoader.item
    
    // Brand Dialogs
    AboutDialog {
        id: aboutDialog
    }
}
