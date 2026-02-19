import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
    
    // Parent handles window properties
    
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
                            width: 40
                            height: 40
                            radius: 8
                            color: syncMouseArea.containsMouse ? "#4b5563" : "#374151"
                            
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
                            Layout.preferredWidth: appController.isAuthenticated ? 200 : 180
                            Layout.preferredHeight: 40
                            color: appController.isAuthenticated ? "transparent" : "#3b82f6"
                            radius: 8
                            border.color: appController.isAuthenticated ? "#4b5563" : "transparent"
                            border.width: appController.isAuthenticated ? 1 : 0
                            
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
                            text: appController.sortAscending ? "ASC" : "DESC"
                            Layout.preferredWidth: parent.compactLayout ? 74 : 82
                            onClicked: appController.toggleSortDirection()
                        }

                        Item {
                            visible: !parent.compactLayout
                            Layout.fillWidth: !parent.compactLayout
                        }

                        Button {
                            text: parent.compactLayout
                                  ? mainContent.tr("Reset", "Reset")
                                  : mainContent.tr("Reset filtri", "Reset filters")
                            Layout.preferredWidth: parent.compactLayout ? 82 : 110
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
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: !!appController.selectedAnime.media
                    clip: true
                    
                    ColumnLayout {
                        width: parent.availableWidth
                        spacing: 20
                        anchors.leftMargin: 5
                        anchors.rightMargin: 5
                        
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
                                text: appController.selectedAnime.display_title || ""
                                color: "#ffffff"
                                font.pixelSize: 24 // Reduced from 28 to give more room
                                font.bold: true
                                wrapMode: Text.WordWrap
                                maximumLineCount: 5
                                elide: Text.ElideNone
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
