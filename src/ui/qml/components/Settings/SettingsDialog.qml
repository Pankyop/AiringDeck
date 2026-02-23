import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDialog
    modal: true
    property bool isEnglishUi: appController.appLanguage === "en"
    readonly property color panelColor: "#2b364a"
    readonly property color panelBorderColor: "#3a4760"
    readonly property color panelSubTextColor: "#9fb0c5"
    
    property point lastMousePos: Qt.point(0, 0)
    function tr(itText, enText) {
        return settingsDialog.isEnglishUi ? enText : itText
    }
    
    onOpened: {
        x = (parent.width - width) / 2
        y = (parent.height - height) / 2
        Qt.callLater(function() {
            uiLanguageCombo.forceActiveFocus()
        })
    }
    Keys.onEscapePressed: settingsDialog.close()
    
    width: 520
    height: 730
    
    standardButtons: Dialog.NoButton
    
    background: Rectangle {
        color: "#182131"
        border.color: "#2d3748"
        border.width: 1
        radius: 20
        
        // Subtle outer glow/shadow
        layer.enabled: true
    }
    
    header: Rectangle {
        color: "#111827"
        height: 70
        radius: 20
        
        MouseArea {
            anchors.fill: parent
            property bool dragActive: false
            
            onPressed: (mouse) => {
                lastMousePos = Qt.point(mouse.x, mouse.y)
                dragActive = true
            }
            onPositionChanged: (mouse) => {
                if (dragActive) {
                    let delta = Qt.point(mouse.x - lastMousePos.x, mouse.y - lastMousePos.y)
                    settingsDialog.x += delta.x
                    settingsDialog.y += delta.y
                }
            }
            onReleased: dragActive = false
            cursorShape: dragActive ? Qt.ClosedHandCursor : Qt.OpenHandCursor
        }

        // Clip the bottom corners of the header
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 20
            color: "#111827"
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 20
            
            Text {
                text: "⚙️ " + settingsDialog.tr("IMPOSTAZIONI", "SETTINGS")
                color: "#ffffff"
                font.pixelSize: 18
                font.bold: true
                font.letterSpacing: 2
            }

            Rectangle {
                Layout.alignment: Qt.AlignVCenter
                Layout.leftMargin: 8
                color: "#0f766e"
                radius: 8
                implicitWidth: noTrackerBadgeText.implicitWidth + 14
                implicitHeight: 24

                Text {
                    id: noTrackerBadgeText
                    anchors.centerIn: parent
                    text: settingsDialog.tr("NO-TRACKER", "NO-TRACKER")
                    color: "#ccfbf1"
                    font.pixelSize: 11
                    font.bold: true
                }
            }
            
            Item { Layout.fillWidth: true }
            
            Button {
                id: headerCloseButton
                implicitWidth: 36
                implicitHeight: 36
                activeFocusOnTab: true
                KeyNavigation.tab: uiLanguageCombo
                KeyNavigation.backtab: closeBtn
                Accessible.role: Accessible.Button
                Accessible.name: settingsDialog.tr("Chiudi impostazioni", "Close settings")
                Accessible.description: settingsDialog.tr(
                                            "Chiude la finestra impostazioni",
                                            "Closes the settings window"
                                        )
                onClicked: settingsDialog.close()

                background: Rectangle {
                    radius: 18
                    color: parent.hovered ? "#334155" : "#2d3748"
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                contentItem: Text {
                    text: "✕"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
    
    contentItem: ColumnLayout {
        spacing: 18
        anchors.margins: 20
        
        // Section: Interface
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: settingsDialog.tr("INTERFACCIA", "INTERFACE")
                color: "#718096"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1.5
            }

            Rectangle {
                Layout.fillWidth: true
                height: 92
                color: settingsDialog.panelColor
                radius: 12
                border.color: settingsDialog.panelBorderColor
                border.width: 1
                clip: true

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: settingsDialog.tr("Lingua applicazione", "Application language")
                            color: "white"
                            font.pixelSize: 15
                            font.bold: true
                        }
                        Text {
                            text: settingsDialog.tr("Cambia i testi dell'interfaccia (IT/EN)", "Change interface texts (IT/EN)")
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }

                    Item { Layout.fillWidth: true }

                    ComboBox {
                        id: uiLanguageCombo
                        Layout.preferredWidth: 172
                        model: [
                            { label: "Italiano", value: "it" },
                            { label: "English", value: "en" }
                        ]
                        textRole: "label"
                        currentIndex: appController.appLanguage === "en" ? 1 : 0
                        activeFocusOnTab: true
                        KeyNavigation.tab: titleSwitch
                        KeyNavigation.backtab: headerCloseButton
                        Accessible.name: settingsDialog.tr("Lingua applicazione", "Application language")
                        Accessible.description: settingsDialog.tr(
                                                    "Seleziona italiano o inglese per i testi dell'interfaccia",
                                                    "Choose Italian or English for interface texts"
                                                )
                        onActivated: appController.appLanguage = model[currentIndex].value
                        contentItem: Text {
                            leftPadding: 10
                            rightPadding: uiLanguageCombo.indicator.width + uiLanguageCombo.spacing
                            text: uiLanguageCombo.displayText
                            color: "#e2e8f0"
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                            font.pixelSize: 14
                        }
                        background: Rectangle {
                            radius: 8
                            color: "#1f2937"
                            border.color: "#475569"
                            border.width: 1
                        }
                        delegate: ItemDelegate {
                            width: uiLanguageCombo.width
                            highlighted: uiLanguageCombo.highlightedIndex === index
                            contentItem: Text {
                                text: modelData.label
                                color: highlighted ? "#ffffff" : "#dbe7f5"
                                elide: Text.ElideRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 13
                            }
                            background: Rectangle {
                                color: highlighted ? "#2563eb" : (parent.hovered ? "#334155" : "#0f172a")
                            }
                        }
                    }
                }
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 86
                color: settingsDialog.panelColor
                radius: 12
                border.color: settingsDialog.panelBorderColor
                border.width: 1
                clip: true
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    
                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: settingsDialog.tr("Titoli in Inglese", "English titles")
                            color: "white"
                            font.pixelSize: 15
                            font.bold: true
                        }
                        Text {
                            text: settingsDialog.tr("Usa nomi occidentali quando disponibili", "Use western names when available")
                            color: settingsDialog.panelSubTextColor
                            font.pixelSize: 12
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Switch {
                        id: titleSwitch
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        Layout.preferredWidth: 70
                        Layout.minimumWidth: 70
                        Layout.maximumWidth: 70
                        implicitWidth: 70
                        implicitHeight: 34
                        leftPadding: 0
                        rightPadding: 0
                        topPadding: 0
                        bottomPadding: 0
                        spacing: 0
                        checked: appController.useEnglishTitle
                        activeFocusOnTab: true
                        KeyNavigation.tab: notificationsSwitch
                        KeyNavigation.backtab: uiLanguageCombo
                        Accessible.name: settingsDialog.tr("Titoli in inglese", "English titles")
                        Accessible.description: settingsDialog.tr(
                                                    "Mostra i titoli in inglese quando disponibili",
                                                    "Show English titles when available"
                                                )
                        onToggled: appController.useEnglishTitle = checked
                        indicator: Rectangle {
                            implicitWidth: 70
                            implicitHeight: 34
                            x: 0
                            y: 0
                            radius: 17
                            color: titleSwitch.checked ? "#10b981" : "#334155"
                            border.color: titleSwitch.checked ? "#0f766e" : "#475569"
                            border.width: 1

                            Rectangle {
                                width: 28
                                height: 28
                                radius: 14
                                y: 3
                                x: titleSwitch.checked ? parent.width - width - 3 : 3
                                color: "#e2e8f0"
                                border.color: "#94a3b8"
                                Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                            }
                        }
                        contentItem: Item { implicitWidth: 0; implicitHeight: 0 }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 110
                color: settingsDialog.panelColor
                radius: 12
                border.color: settingsDialog.panelBorderColor
                border.width: 1
                clip: true

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: settingsDialog.tr("Notifiche prossimi episodi", "Upcoming episode notifications")
                            color: "white"
                            font.pixelSize: 15
                            font.bold: true
                        }
                        Text {
                            text: settingsDialog.tr("Avvisa prima dell'uscita", "Alert before episode airing")
                            color: settingsDialog.panelSubTextColor
                            font.pixelSize: 12
                        }
                    }

                    Item { Layout.fillWidth: true }

                    ColumnLayout {
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        Layout.preferredWidth: 132
                        spacing: 6
                        Switch {
                            id: notificationsSwitch
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 70
                            Layout.minimumWidth: 70
                            Layout.maximumWidth: 70
                            implicitWidth: 70
                            implicitHeight: 34
                            leftPadding: 0
                            rightPadding: 0
                            topPadding: 0
                            bottomPadding: 0
                            spacing: 0
                            checked: appController.notificationsEnabled
                            activeFocusOnTab: true
                            KeyNavigation.tab: notificationsSwitch.checked ? notifyLeadCombo : updateChecksSwitch
                            KeyNavigation.backtab: titleSwitch
                            Accessible.name: settingsDialog.tr(
                                                 "Notifiche prossimi episodi",
                                                 "Upcoming episode notifications"
                                             )
                            Accessible.description: settingsDialog.tr(
                                                        "Attiva o disattiva le notifiche dei prossimi episodi",
                                                        "Enable or disable upcoming episode notifications"
                                                    )
                            onToggled: appController.notificationsEnabled = checked
                            indicator: Rectangle {
                                implicitWidth: 70
                                implicitHeight: 34
                                x: 0
                                y: 0
                                radius: 17
                                color: notificationsSwitch.checked ? "#10b981" : "#334155"
                                border.color: notificationsSwitch.checked ? "#0f766e" : "#475569"
                                border.width: 1

                                Rectangle {
                                    width: 28
                                    height: 28
                                    radius: 14
                                    y: 3
                                    x: notificationsSwitch.checked ? parent.width - width - 3 : 3
                                    color: "#e2e8f0"
                                    border.color: "#94a3b8"
                                    Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                                }
                            }
                            contentItem: Item { implicitWidth: 0; implicitHeight: 0 }
                        }

                        ComboBox {
                            id: notifyLeadCombo
                            enabled: notificationsSwitch.checked
                            Layout.preferredWidth: 132
                            activeFocusOnTab: true
                            KeyNavigation.tab: updateChecksSwitch
                            KeyNavigation.backtab: notificationsSwitch
                            Accessible.name: settingsDialog.tr(
                                                 "Anticipo notifica",
                                                 "Notification lead time"
                                             )
                            Accessible.description: settingsDialog.tr(
                                                        "Seleziona quanti minuti prima ricevere la notifica",
                                                        "Select how many minutes before to receive the notification"
                                                    )
                            model: [
                                { label: "5 min", value: 5 },
                                { label: "15 min", value: 15 },
                                { label: "30 min", value: 30 },
                                { label: "60 min", value: 60 }
                            ]
                            textRole: "label"
                            currentIndex: {
                                for (var i = 0; i < model.length; i++) {
                                    if (model[i].value === appController.notificationLeadMinutes) {
                                        return i
                                    }
                                }
                                return 1
                            }
                            onActivated: appController.notificationLeadMinutes = model[currentIndex].value
                            contentItem: Text {
                                leftPadding: 10
                                rightPadding: notifyLeadCombo.indicator.width + notifyLeadCombo.spacing
                                text: notifyLeadCombo.displayText
                                color: notifyLeadCombo.enabled ? "#e2e8f0" : "#64748b"
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                                font.pixelSize: 13
                            }
                            background: Rectangle {
                                radius: 8
                                color: notifyLeadCombo.enabled ? "#1f2937" : "#111827"
                                border.color: notifyLeadCombo.enabled ? "#475569" : "#334155"
                                border.width: 1
                            }
                            delegate: ItemDelegate {
                                width: notifyLeadCombo.width
                                highlighted: notifyLeadCombo.highlightedIndex === index
                                contentItem: Text {
                                    text: modelData.label
                                    color: highlighted ? "#ffffff" : "#dbe7f5"
                                    elide: Text.ElideRight
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                }
                                background: Rectangle {
                                    color: highlighted ? "#2563eb" : (parent.hovered ? "#334155" : "#0f172a")
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 160
                color: settingsDialog.panelColor
                radius: 12
                border.color: settingsDialog.panelBorderColor
                border.width: 1
                clip: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                Layout.fillWidth: true
                                text: settingsDialog.tr("Controllo aggiornamenti", "Update checks")
                                color: "white"
                                font.pixelSize: 14
                                font.bold: true
                            }
                            Text {
                                Layout.fillWidth: true
                                text: settingsDialog.tr("Verifica nuove versioni su GitHub all'avvio", "Check GitHub for new versions at startup")
                                color: settingsDialog.panelSubTextColor
                                font.pixelSize: 11
                                wrapMode: Text.WordWrap
                            }
                        }
                        Switch {
                            id: updateChecksSwitch
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 70
                            Layout.minimumWidth: 70
                            Layout.maximumWidth: 70
                            implicitWidth: 70
                            implicitHeight: 34
                            leftPadding: 0
                            rightPadding: 0
                            topPadding: 0
                            bottomPadding: 0
                            spacing: 0
                            checked: appController.updateChecksEnabled
                            activeFocusOnTab: true
                            KeyNavigation.tab: diagnosticsSwitch
                            KeyNavigation.backtab: notificationsSwitch.checked ? notifyLeadCombo : notificationsSwitch
                            Accessible.name: settingsDialog.tr("Controllo aggiornamenti", "Update checks")
                            Accessible.description: settingsDialog.tr(
                                                        "Abilita o disabilita il controllo aggiornamenti su GitHub",
                                                        "Enable or disable GitHub update checks"
                                                    )
                            onToggled: appController.updateChecksEnabled = checked
                            indicator: Rectangle {
                                implicitWidth: 70
                                implicitHeight: 34
                                x: 0
                                y: 0
                                radius: 17
                                color: updateChecksSwitch.checked ? "#10b981" : "#334155"
                                border.color: updateChecksSwitch.checked ? "#0f766e" : "#475569"
                                border.width: 1

                                Rectangle {
                                    width: 28
                                    height: 28
                                    radius: 14
                                    y: 3
                                    x: updateChecksSwitch.checked ? parent.width - width - 3 : 3
                                    color: "#e2e8f0"
                                    border.color: "#94a3b8"
                                    Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                                }
                            }
                            contentItem: Item { implicitWidth: 0; implicitHeight: 0 }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#3e4b62"
                        opacity: 0.7
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                Layout.fillWidth: true
                                text: settingsDialog.tr("Diagnostica locale", "Local diagnostics")
                                color: "white"
                                font.pixelSize: 14
                                font.bold: true
                            }
                            Text {
                                Layout.fillWidth: true
                                text: settingsDialog.tr("Aggiunge log locali, senza telemetria remota", "Adds local logs, with no remote telemetry")
                                color: settingsDialog.panelSubTextColor
                                font.pixelSize: 11
                                wrapMode: Text.WordWrap
                            }
                        }
                        Switch {
                            id: diagnosticsSwitch
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 70
                            Layout.minimumWidth: 70
                            Layout.maximumWidth: 70
                            implicitWidth: 70
                            implicitHeight: 34
                            leftPadding: 0
                            rightPadding: 0
                            topPadding: 0
                            bottomPadding: 0
                            spacing: 0
                            checked: appController.diagnosticsEnabled
                            activeFocusOnTab: true
                            KeyNavigation.tab: authBtn
                            KeyNavigation.backtab: updateChecksSwitch
                            Accessible.name: settingsDialog.tr("Diagnostica locale", "Local diagnostics")
                            Accessible.description: settingsDialog.tr(
                                                        "Abilita log diagnostici locali senza invio telemetria",
                                                        "Enable local diagnostic logging without telemetry upload"
                                                    )
                            onToggled: appController.diagnosticsEnabled = checked
                            indicator: Rectangle {
                                implicitWidth: 70
                                implicitHeight: 34
                                x: 0
                                y: 0
                                radius: 17
                                color: diagnosticsSwitch.checked ? "#10b981" : "#334155"
                                border.color: diagnosticsSwitch.checked ? "#0f766e" : "#475569"
                                border.width: 1

                                Rectangle {
                                    width: 28
                                    height: 28
                                    radius: 14
                                    y: 3
                                    x: diagnosticsSwitch.checked ? parent.width - width - 3 : 3
                                    color: "#e2e8f0"
                                    border.color: "#94a3b8"
                                    Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                                }
                            }
                            contentItem: Item { implicitWidth: 0; implicitHeight: 0 }
                        }
                    }
                }
            }
        }
        
        // Section: Profilo
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: settingsDialog.tr("PROFILO ANILIST", "ANILIST PROFILE")
                color: "#718096"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1.5
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 90
                color: settingsDialog.panelColor
                radius: 12
                border.color: settingsDialog.panelBorderColor
                border.width: 1
                clip: true
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 16
                    
                    Rectangle {
                        width: 54
                        height: 54
                        radius: 27
                        color: "#1a202c"
                        clip: true
                        border.color: "#4a5568"
                        border.width: 2
                        
                        Image {
                            anchors.fill: parent
                            source: appController.userAvatar
                            fillMode: Image.PreserveAspectCrop
                        }
                    }
                    
                    ColumnLayout {
                        spacing: 2
                        Text {
                            text: appController.isAuthenticated ? appController.userInfo.name : settingsDialog.tr("Non connesso", "Not connected")
                            color: "white"
                            font.bold: true
                            font.pixelSize: 17
                        }
                        Text {
                            text: appController.isAuthenticated
                                  ? settingsDialog.tr("Sincronizzazione attiva", "Active synchronization")
                                  : settingsDialog.tr("Accedi per vedere i tuoi anime", "Login to view your anime list")
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        id: authBtn
                        text: appController.isAuthenticated
                              ? settingsDialog.tr("Logout", "Logout")
                              : settingsDialog.tr("Login", "Login")
                        implicitWidth: 100
                        implicitHeight: 38
                        activeFocusOnTab: true
                        KeyNavigation.tab: closeBtn
                        KeyNavigation.backtab: diagnosticsSwitch
                        Accessible.role: Accessible.Button
                        Accessible.name: appController.isAuthenticated
                                         ? settingsDialog.tr("Esegui logout", "Perform logout")
                                         : settingsDialog.tr("Esegui login", "Perform login")
                        
                        background: Rectangle {
                            color: appController.isAuthenticated ? "transparent" : "#3182ce"
                            radius: 10
                            border.color: appController.isAuthenticated ? "#e53e3e" : "transparent"
                            border.width: 1
                            opacity: authBtn.hovered ? 1.0 : 0.92
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (appController.isAuthenticated) {
                                appController.logout()
                            } else {
                                appController.login()
                                settingsDialog.close()
                            }
                        }
                    }
                }
            }
        }
        
        Item { Layout.fillHeight: true }
        
        // Footer info
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 4
            opacity: 0.5
            
            Text {
                text: "AiringDeck v" + appController.appVersion
                color: "white"
                font.pixelSize: 11
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: settingsDialog.tr("Creato con PySide6 & QML", "Built with PySide6 & QML")
                color: "#a0aec0"
                font.pixelSize: 10
                Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Button {
            id: closeBtn
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 220
            Layout.preferredHeight: 46
            text: settingsDialog.tr("CONFERMA E CHIUDI", "CONFIRM AND CLOSE")
            activeFocusOnTab: true
            KeyNavigation.tab: headerCloseButton
            KeyNavigation.backtab: authBtn
            Accessible.role: Accessible.Button
            Accessible.name: settingsDialog.tr("Conferma e chiudi", "Confirm and close")
            Accessible.description: settingsDialog.tr(
                                        "Salva le impostazioni correnti e chiude la finestra",
                                        "Saves current settings and closes the window"
                                    )
            
            background: Rectangle {
                color: closeBtn.hovered ? "#2563eb" : "#1d4ed8"
                radius: 10
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                font.bold: true
                font.pixelSize: 13
                font.letterSpacing: 1
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: settingsDialog.close()
        }
    }
}
