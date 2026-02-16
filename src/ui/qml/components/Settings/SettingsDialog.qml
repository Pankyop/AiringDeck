import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: settingsDialog
    modal: true
    
    property point lastMousePos: Qt.point(0, 0)
    
    onOpened: {
        x = (parent.width - width) / 2
        y = (parent.height - height) / 2
    }
    
    width: 480
    height: 520
    
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
                text: "⚙️ IMPOSTAZIONI"
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
                text: "INTERFACCIA"
                color: "#718096"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1.5
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
                            text: "Titoli in Inglese"
                            color: "white"
                            font.pixelSize: 15
                            font.bold: true
                        }
                        Text {
                            text: "Usa nomi occidentali quando disponibili"
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Switch {
                        id: titleSwitch
                        checked: appController.useEnglishTitle
                        onToggled: appController.useEnglishTitle = checked
                    }
                }
            }
        }
        
        // Section: Profilo
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: "PROFILO ANILIST"
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
                            text: appController.isAuthenticated ? appController.userInfo.name : "Non Connesso"
                            color: "white"
                            font.bold: true
                            font.pixelSize: 17
                        }
                        Text {
                            text: appController.isAuthenticated ? "Sincronizzazione Attiva" : "Accedi per vedere i tuoi anime"
                            color: "#a0aec0"
                            font.pixelSize: 12
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        id: authBtn
                        text: appController.isAuthenticated ? "Logout" : "Login"
                        implicitWidth: 100
                        implicitHeight: 38
                        
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
                text: "AiringDeck v" + appController.appVersion + " Beta"
                color: "white"
                font.pixelSize: 11
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: "Creato con PySide6 & QML"
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
            text: "CONFERMA E CHIUDI"
            
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
