import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: aboutDialog
    modal: true
    title: appController.appLanguage === "en" ? "About AiringDeck" : "Informazioni su AiringDeck"
    
    width: 400
    height: 450
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    
    background: Rectangle {
        color: "#1a1f26"
        radius: 20
        border.color: "#374151"
        border.width: 1
    }
    
    header: Item { height: 0 } // No standard header
    
    contentItem: ColumnLayout {
        spacing: 20
        anchors.margins: 30
        
        Logo {
            Layout.alignment: Qt.AlignHCenter
            width: 120
            height: 120
            primaryColor: "#34d399"
        }
        
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 5
            
            Text {
                text: "AiringDeck"
                color: "#ffffff"
                font.pixelSize: 28
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "v" + appController.appVersion + " Beta"
                color: "#34d399"
                font.pixelSize: 16
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#374151"
            opacity: 0.5
        }
        
        Text {
            Layout.fillWidth: true
            text: appController.appLanguage === "en"
                  ? "A modern and high-performance desktop tracker for your anime releases, integrated with AniList."
                  : "Un tracker desktop moderno e performante per le tue uscite anime, integrato con AniList."
            color: "#9ca3af"
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        
        Item { Layout.fillHeight: true }
        
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 2
            
            Text {
                text: "Developed by Antigravity"
                color: "#6b7280"
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: appController.appLanguage === "en" ? "Built with PySide6 & QML" : "Creato con PySide6 & QML"
                color: "#4b5563"
                font.pixelSize: 11
                Layout.alignment: Qt.AlignHCenter
            }
        }
        
        Button {
            text: appController.appLanguage === "en" ? "CLOSE" : "CHIUDI"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 120
            onClicked: aboutDialog.close()
            
            background: Rectangle {
                color: parent.down ? "#059669" : (parent.hovered ? "#10b981" : "#065f46")
                radius: 10
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
