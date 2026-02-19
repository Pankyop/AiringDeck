import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDialog
    modal: true
    property bool isEnglishUi: appController.appLanguage === "en"
    
    property point lastMousePos: Qt.point(0, 0)
    function tr(itText, enText) {
        return settingsDialog.isEnglishUi ? enText : itText
    }
    
    onOpened: {
        x = (parent.width - width) / 2
        y = (parent.height - height) / 2
    }
    
    width: 480
    height: 620
    
    standardButtons: Dialog.NoButton
    
    background: Rectangle {
        color: "#1a1f26" 
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
            
            Item { Layout.fillWidth: true }
            
            // Re-styled Close Button
            Rectangle {
                width: 36
                height: 36
                radius: 18
                color: closeMA.containsMouse ? "#ef4444" : "#2d3748"
                
                Text {
                    anchors.centerIn: parent
                    text: "✕"
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                }
                
                MouseArea {
                    id: closeMA
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: settingsDialog.close()
                }
                
                Behavior on color { ColorAnimation { duration: 150 } }
            }
        }
    }
    
    contentItem: ColumnLayout {
        spacing: 20
        anchors.margins: 30
        
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
                height: 82
                color: "#2d3748"
                radius: 12
                opacity: 0.8

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
                        Layout.preferredWidth: 150
                        model: [
                            { label: "Italiano", value: "it" },
                            { label: "English", value: "en" }
                        ]
                        textRole: "label"
                        currentIndex: appController.appLanguage === "en" ? 1 : 0
                        activeFocusOnTab: true
                        Accessible.name: settingsDialog.tr("Lingua applicazione", "Application language")
                        onActivated: appController.appLanguage = model[currentIndex].value
                    }
                }
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 70
                color: "#2d3748"
                radius: 12
                opacity: 0.8
                
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
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Switch {
                        id: titleSwitch
                        checked: appController.useEnglishTitle
                        activeFocusOnTab: true
                        Accessible.name: settingsDialog.tr("Titoli in inglese", "English titles")
                        onToggled: appController.useEnglishTitle = checked
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 98
                color: "#2d3748"
                radius: 12
                opacity: 0.8

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
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }

                    Item { Layout.fillWidth: true }

                    ColumnLayout {
                        spacing: 6
                        Switch {
                            id: notificationsSwitch
                            checked: appController.notificationsEnabled
                            activeFocusOnTab: true
                            Accessible.name: settingsDialog.tr(
                                                 "Notifiche prossimi episodi",
                                                 "Upcoming episode notifications"
                                             )
                            onToggled: appController.notificationsEnabled = checked
                        }

                        ComboBox {
                            id: notifyLeadCombo
                            enabled: notificationsSwitch.checked
                            Layout.preferredWidth: 120
                            activeFocusOnTab: true
                            Accessible.name: settingsDialog.tr(
                                                 "Anticipo notifica",
                                                 "Notification lead time"
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
                color: "#2d3748"
                radius: 12
                opacity: 0.8
                
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
                        Accessible.role: Accessible.Button
                        Accessible.name: appController.isAuthenticated
                                         ? settingsDialog.tr("Esegui logout", "Perform logout")
                                         : settingsDialog.tr("Esegui login", "Perform login")
                        
                        background: Rectangle {
                            color: appController.isAuthenticated ? "transparent" : "#3182ce"
                            radius: 8
                            border.color: appController.isAuthenticated ? "#e53e3e" : "transparent"
                            border.width: 1
                            opacity: authBtn.hovered ? 1.0 : 0.9
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
            Layout.preferredWidth: 200
            Layout.preferredHeight: 45
            text: settingsDialog.tr("CONFERMA E CHIUDI", "CONFIRM AND CLOSE")
            activeFocusOnTab: true
            Accessible.role: Accessible.Button
            Accessible.name: settingsDialog.tr("Conferma e chiudi", "Confirm and close")
            
            background: Rectangle {
                color: closeBtn.hovered ? "#4a5568" : "#2d3748"
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
