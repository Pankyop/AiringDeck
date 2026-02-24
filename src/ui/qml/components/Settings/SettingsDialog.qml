import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDialog
    modal: true
    property bool isEnglishUi: appController.appLanguage === "en"
    readonly property color panelColor: "#283a55"
    readonly property color panelBorderColor: "#425c7f"
    readonly property color panelSubTextColor: "#a8bdd5"
    readonly property color sectionLabelColor: "#7f9bbb"
    readonly property color accentColor: "#3b82f6"
    readonly property color accentSoftColor: "#60a5fa"
    
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
    
    width: 1180
    height: 680
    
    standardButtons: Dialog.NoButton
    
    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0f1a2c" }
            GradientStop { position: 1.0; color: "#1a2b44" }
        }
        border.color: "#355079"
        border.width: 1
        radius: 22
        
        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 21
            color: "transparent"
            border.color: "#253852"
            border.width: 1
            opacity: 0.8
        }
    }
    
    header: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0d1730" }
            GradientStop { position: 1.0; color: "#12213e" }
        }
        height: 80
        radius: 22
        
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
            color: "#12213e"
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 24
            anchors.rightMargin: 20
            
            ColumnLayout {
                spacing: 2

                Text {
                    text: "⚙️ " + settingsDialog.tr("IMPOSTAZIONI", "SETTINGS")
                    color: "#ffffff"
                    font.pixelSize: 20
                    font.bold: true
                    font.letterSpacing: 2.4
                }
                Text {
                    text: settingsDialog.tr("Controlli locali e privacy", "Local controls and privacy")
                    color: "#9db0cb"
                    font.pixelSize: 11
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignVCenter
                Layout.leftMargin: 8
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#0891b2" }
                    GradientStop { position: 1.0; color: "#0f766e" }
                }
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
                    color: parent.hovered ? "#334155" : "#26354d"
                    border.color: parent.hovered ? settingsDialog.accentSoftColor : "#425a7a"
                    border.width: 1
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
    
    contentItem: Rectangle {
        color: "#11233d"
        radius: 18
        border.color: "#2f4f77"
        border.width: 1
        clip: true

        GridLayout {
            columns: 2
            columnSpacing: 24
            rowSpacing: 12
            anchors.fill: parent
            anchors.margins: 16
            
            // Section: Interface
            ColumnLayout {
            Layout.row: 0
            Layout.column: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: 760
            spacing: 0
            
            Text {
                text: settingsDialog.tr("INTERFACCIA", "INTERFACE")
                color: settingsDialog.sectionLabelColor
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 2.2
            }

            Item { Layout.preferredHeight: 6 }

            Rectangle {
                Layout.fillWidth: true
                height: 86
                color: "transparent"
                radius: 0
                border.color: "transparent"
                border.width: 0
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
                Layout.preferredHeight: 1
                color: "#35516f"
                opacity: 0.78
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 82
                color: "transparent"
                radius: 0
                border.color: "transparent"
                border.width: 0
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
                Layout.preferredHeight: 1
                color: "#35516f"
                opacity: 0.78
            }

            Rectangle {
                Layout.fillWidth: true
                height: 106
                color: "transparent"
                radius: 0
                border.color: "transparent"
                border.width: 0
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
                            KeyNavigation.tab: notificationsSwitch.checked ? notifyLeadCombo : checkUpdatesNowButton
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
                            KeyNavigation.tab: checkUpdatesNowButton
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

            Item { Layout.preferredHeight: 14 }

            Text {
                text: settingsDialog.tr("SERVIZI RETE", "NETWORK SERVICES")
                color: settingsDialog.sectionLabelColor
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 2.2
            }

            Item { Layout.preferredHeight: 6 }

            Rectangle {
                Layout.fillWidth: true
                height: 208
                color: "transparent"
                radius: 0
                border.color: "transparent"
                border.width: 0
                clip: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 4
                    spacing: 0

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
                        Button {
                            id: checkUpdatesNowButton
                            text: settingsDialog.tr("Controlla ora", "Check now")
                            Layout.preferredWidth: 110
                            activeFocusOnTab: true
                            KeyNavigation.tab: appController.devProfileMode ? testNotificationButton : updateChecksSwitch
                            KeyNavigation.backtab: notificationsSwitch.checked ? notifyLeadCombo : notificationsSwitch
                            Accessible.role: Accessible.Button
                            Accessible.name: settingsDialog.tr("Controlla aggiornamenti ora", "Check updates now")
                            Accessible.description: settingsDialog.tr(
                                                        "Esegue una verifica immediata della disponibilita di nuove versioni",
                                                        "Runs an immediate check for new versions"
                                                    )
                            onClicked: appController.checkForUpdates()
                            background: Rectangle {
                                radius: 8
                                color: checkUpdatesNowButton.hovered ? "#2563eb" : "#1d4ed8"
                                border.color: "#3b82f6"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: checkUpdatesNowButton.text
                                color: "#ffffff"
                                font.pixelSize: 12
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        Button {
                            id: testNotificationButton
                            text: settingsDialog.tr("Notifica test", "Test notify")
                            Layout.preferredWidth: 104
                            visible: appController.devProfileMode
                            enabled: appController.devProfileMode
                            activeFocusOnTab: true
                            KeyNavigation.tab: updateChecksSwitch
                            KeyNavigation.backtab: checkUpdatesNowButton
                            Accessible.role: Accessible.Button
                            Accessible.name: settingsDialog.tr("Invia notifica di test", "Send test notification")
                            Accessible.description: settingsDialog.tr(
                                                        "Invia una notifica locale di prova",
                                                        "Sends a local test notification"
                                                    )
                            onClicked: appController.sendTestNotification()
                            background: Rectangle {
                                radius: 8
                                color: testNotificationButton.hovered ? "#334155" : "#1f2937"
                                border.color: "#475569"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: testNotificationButton.text
                                color: "#e2e8f0"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
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
                            KeyNavigation.backtab: appController.devProfileMode ? testNotificationButton : checkUpdatesNowButton
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
                        color: "#35516f"
                        opacity: 0.7
                    }

                    Text {
                        Layout.fillWidth: true
                        Layout.topMargin: 10
                        Layout.bottomMargin: 10
                        text: appController.devProfileMode
                              ? settingsDialog.tr(
                                    "Azioni rapide: verifica aggiornamenti o prova notifica locale.",
                                    "Quick actions: check updates or send a local test notification."
                                )
                              : settingsDialog.tr(
                                    "Azione rapida: verifica aggiornamenti.",
                                    "Quick action: check updates."
                                )
                        color: "#8ea4bf"
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: "#35516f"
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
            Layout.row: 0
            Layout.column: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: 320
            Layout.alignment: Qt.AlignTop
            spacing: 0
            
            Text {
                text: settingsDialog.tr("PROFILO ANILIST", "ANILIST PROFILE")
                color: settingsDialog.sectionLabelColor
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 2.2
            }

            Item { Layout.preferredHeight: 6 }
            
            Rectangle {
                Layout.fillWidth: true
                height: 88
                color: "transparent"
                radius: 0
                border.color: "transparent"
                border.width: 0
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

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: "#35516f"
                opacity: 0.78
            }
        }
        
        Item {
            Layout.row: 1
            Layout.column: 0
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
        
        // Footer info
        ColumnLayout {
            Layout.row: 1
            Layout.column: 1
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 10
            spacing: 4
            opacity: 0.56
            
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
            Layout.row: 2
            Layout.column: 1
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 228
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
                border.color: "#3b82f6"
                border.width: 1
                color: closeBtn.hovered ? "#2563eb" : "#1d4ed8"
                radius: 12
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
}
