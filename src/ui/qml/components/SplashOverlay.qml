import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: splashOverlay
    anchors.fill: parent
    color: "#0f172a" // Dark Slate background
    z: 9999 // Ensure it's on top
    
    property bool active: appController.isLoading
    
    // Fade out when loading finishes
    opacity: active ? 1.0 : 0.0
    visible: opacity > 0
    
    Behavior on opacity {
        NumberAnimation { duration: 800; easing.type: Easing.InOutQuart }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 30
        
        // Central Logo with Pulse Animation
        Logo {
            id: centralLogo
            Layout.alignment: Qt.AlignHCenter
            width: 140
            height: 140
            primaryColor: "#34d399"
            
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 1.1; duration: 2000; easing.type: Easing.InOutQuad }
                NumberAnimation { from: 1.1; to: 1.0; duration: 2000; easing.type: Easing.InOutQuad }
            }
        }
        
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 12
            
            Text {
                text: "AIRINGDECK"
                color: "white"
                font.pixelSize: 24
                font.bold: true
                font.letterSpacing: 4
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: appController.statusMessage || (appController.appLanguage === "en" ? "Synchronizing data..." : "Sincronizzazione dati...")
                color: "#64748b"
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
                
                // Subtle fade loop for message
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 0.4; duration: 1000; easing.type: Easing.InOutSine }
                    NumberAnimation { from: 0.4; to: 1.0; duration: 1000; easing.type: Easing.InOutSine }
                }
            }
        }
    }
    
    // Interactive block (prevent clicks on UI behind splash)
    MouseArea {
        anchors.fill: parent
        enabled: splashOverlay.visible
    }
}
