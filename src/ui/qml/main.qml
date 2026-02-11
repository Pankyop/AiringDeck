import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: mainWindow
    
    width: 1400
    height: 900
    minimumWidth: 1024
    minimumHeight: 768
    visible: true
    title: "Anime Calendar"
    
    // Color scheme
    color: "#1f2937"
    
    // Main layout
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
                            
                            Text {
                                text: "🎬"
                                font.pixelSize: 32
                            }
                            
                            Text {
                                text: "Anime Calendar"
                                font.pixelSize: 24
                                font.bold: true
                                color: "#ffffff"
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        // Search bar
                        Rectangle {
                            Layout.preferredWidth: 400
                            Layout.preferredHeight: 40
                            color: "#374151"
                            radius: 8
                            
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
                                    Layout.fillWidth: true
                                    color: "#ffffff"
                                    font.pixelSize: 14
                                    verticalAlignment: Text.AlignVCenter
                                    
                                    Text {
                                        text: "Search anime to follow..."
                                        color: "#6b7280"
                                        visible: parent.text.length === 0
                                        font.pixelSize: 14
                                    }
                                }
                            }
                        }
                        
                        // Login/Profile
                        Rectangle {
                            Layout.preferredWidth: appController.isAuthenticated ? 200 : 180
                            Layout.preferredHeight: 40
                            color: appController.isAuthenticated ? "transparent" : "#3b82f6"
                            radius: 8
                            border.color: appController.isAuthenticated ? "#4b5563" : "transparent"
                            border.width: appController.isAuthenticated ? 1 : 0
                            
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (appController.isAuthenticated) {
                                        // TODO: Show dropdown menu
                                    } else {
                                        appController.login()
                                    }
                                }
                            }
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                spacing: 10
                                
                                // Avatar (when logged in)
                                Rectangle {
                                    Layout.preferredWidth: 32
                                    Layout.preferredHeight: 32
                                    radius: 16
                                    color: "#6b7280"
                                    visible: appController.isAuthenticated
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "👤"
                                        font.pixelSize: 20
                                    }
                                }
                                
                                Text {
                                    text: appController.isAuthenticated ? "Username" : "🔐 Login with AniList"
                                    color: "#ffffff"
                                    font.pixelSize: 14
                                    font.bold: !appController.isAuthenticated
                                }
                                
                                // Dropdown arrow (when logged in)
                                Text {
                                    text: "▼"
                                    color: "#9ca3af"
                                    font.pixelSize: 10
                                    visible: appController.isAuthenticated
                                }
                            }
                        }
                    }
                }
                
                // Calendar placeholder
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#111827"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "📅 Calendar will be here\n\n(Qt QML Calendar Component)"
                        color: "#6b7280"
                        font.pixelSize: 18
                        horizontalAlignment: Text.AlignHCenter
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
                
                Text {
                    text: "Episode Details"
                    font.pixelSize: 20
                    font.bold: true
                    color: "#ffffff"
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#111827"
                    radius: 8
                    
                    Text {
                        anchors.centerIn: parent
                        text: "📺 Episode details\nwill appear here"
                        color: "#6b7280"
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignHCenter
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
                text: appController.isAuthenticated ? "✅ Connected to AniList" : "⚠️ Not authenticated"
                color: appController.isAuthenticated ? "#10b981" : "#f59e0b"
                font.pixelSize: 12
            }
            
            Item { Layout.fillWidth: true }
            
            Text {
                text: "Qt " + Qt.version
                color: "#6b7280"
                font.pixelSize: 11
            }
        }
    }
}
