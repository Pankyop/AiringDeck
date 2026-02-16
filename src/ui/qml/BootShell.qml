import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

import "components"

ApplicationWindow {
    id: bootWindow
    width: 1400
    height: 900
    minimumWidth: 1024
    minimumHeight: 768
    visible: true
    title: "AiringDeck"
    color: "#0f172a"
    flags: Qt.FramelessWindowHint | Qt.Window | Qt.WindowMinMaxButtonsHint

    readonly property bool isMaximized: bootWindow.visibility === Window.Maximized

    function toggleMaximize() {
        if (bootWindow.visibility === Window.Maximized) {
            bootWindow.showNormal()
        } else {
            bootWindow.showMaximized()
        }
    }

    // ─── Custom Title Bar ───
    Rectangle {
        id: titleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 36
        color: "#1a1f2e"
        z: 10000

        // Draggable area
        MouseArea {
            id: dragArea
            anchors.fill: parent
            onPressed: bootWindow.startSystemMove()
            onDoubleClicked: bootWindow.toggleMaximize()
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 4
            spacing: 0

            // App Icon (small)
            Logo {
                width: 20
                height: 20
                primaryColor: "#34d399"
            }

            // Title Text
            Text {
                text: "  AiringDeck"
                color: "#94a3b8"
                font.pixelSize: 13
                font.family: "Segoe UI"
                Layout.fillWidth: true
            }

            // ── Window Controls ──

            // Minimize
            Rectangle {
                id: minimizeBtn
                width: 46
                height: 36
                color: minimizeArea.containsMouse ? "#2a3040" : "transparent"
                
                Text {
                    anchors.centerIn: parent
                    text: "─"
                    color: "#94a3b8"
                    font.pixelSize: 13
                }
                
                MouseArea {
                    id: minimizeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: bootWindow.showMinimized()
                }
            }

            // Maximize / Restore
            Rectangle {
                id: maximizeBtn
                width: 46
                height: 36
                color: maximizeArea.containsMouse ? "#2a3040" : "transparent"
                
                Text {
                    anchors.centerIn: parent
                    text: bootWindow.isMaximized ? "❐" : "□"
                    color: "#94a3b8"
                    font.pixelSize: bootWindow.isMaximized ? 12 : 16
                }
                
                MouseArea {
                    id: maximizeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: bootWindow.toggleMaximize()
                }
            }

            // Close
            Rectangle {
                id: closeBtn
                width: 46
                height: 36
                color: closeArea.containsMouse ? "#e81123" : "transparent"
                radius: closeArea.containsMouse ? 0 : 0
                
                Text {
                    anchors.centerIn: parent
                    text: "✕"
                    color: closeArea.containsMouse ? "white" : "#94a3b8"
                    font.pixelSize: 13
                }
                
                MouseArea {
                    id: closeArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: bootWindow.close()
                }
            }
        }

        // Bottom border
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: "#2a3040"
        }
    }

    // ─── Window Resize Handles ───
    // Bottom-right corner
    MouseArea {
        id: resizeBR
        width: 8; height: 8
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeFDiagCursor
        z: 10001
        property point clickPos
        onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
        onPositionChanged: function(mouse) {
            if (pressed && !bootWindow.isMaximized) {
                var newW = Math.max(bootWindow.minimumWidth, bootWindow.width + mouse.x - clickPos.x)
                var newH = Math.max(bootWindow.minimumHeight, bootWindow.height + mouse.y - clickPos.y)
                bootWindow.width = newW
                bootWindow.height = newH
            }
        }
    }
    // Right edge
    MouseArea {
        width: 5
        anchors.right: parent.right
        anchors.top: titleBar.bottom
        anchors.bottom: resizeBR.top
        cursorShape: Qt.SizeHorCursor
        z: 10001
        property point clickPos
        onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
        onPositionChanged: function(mouse) {
            if (pressed && !bootWindow.isMaximized) {
                bootWindow.width = Math.max(bootWindow.minimumWidth, bootWindow.width + mouse.x - clickPos.x)
            }
        }
    }
    // Bottom edge
    MouseArea {
        height: 5
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: resizeBR.left
        cursorShape: Qt.SizeVerCursor
        z: 10001
        property point clickPos
        onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
        onPositionChanged: function(mouse) {
            if (pressed && !bootWindow.isMaximized) {
                bootWindow.height = Math.max(bootWindow.minimumHeight, bootWindow.height + mouse.y - clickPos.y)
            }
        }
    }
    // Left edge
    MouseArea {
        width: 5
        anchors.left: parent.left
        anchors.top: titleBar.bottom
        anchors.bottom: parent.bottom
        cursorShape: Qt.SizeHorCursor
        z: 10001
        property point clickPos
        onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
        onPositionChanged: function(mouse) {
            if (pressed && !bootWindow.isMaximized) {
                var dx = mouse.x - clickPos.x
                if (bootWindow.width - dx >= bootWindow.minimumWidth) {
                    bootWindow.x += dx
                    bootWindow.width -= dx
                }
            }
        }
    }
    // Top edge
    MouseArea {
        height: 5
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        cursorShape: Qt.SizeVerCursor
        z: 10001
        property point clickPos
        onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
        onPositionChanged: function(mouse) {
            if (pressed && !bootWindow.isMaximized) {
                var dy = mouse.y - clickPos.y
                if (bootWindow.height - dy >= bootWindow.minimumHeight) {
                    bootWindow.y += dy
                    bootWindow.height -= dy
                }
            }
        }
    }

    // ─── Main Content Area (below title bar) ───

    // 1. Show Splash Immediately (Embedded for maximum speed)
    SplashOverlay {
        id: startupSplash
        anchors.topMargin: titleBar.height
        z: 9999
    }

    // 2. Load Main Content Asynchronously
    Loader {
        id: mainLoader
        anchors.fill: parent
        anchors.topMargin: titleBar.height
        active: false
        source: "MainContent.qml"
        asynchronous: true

        onStatusChanged: {
            if (status === Loader.Ready) {
                console.log("Main content loaded asynchronously")
            }
        }
    }

    // Delay the start of heavy loading
    Timer {
        interval: 50
        running: true
        repeat: false
        onTriggered: {
            mainLoader.active = true
            appController.initialize()
        }
    }
}
