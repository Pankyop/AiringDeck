import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

Item {
    id: root
    width: 200
    height: 320
    property bool isEnglishUi: appController.appLanguage === "en"
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: displayTitle
    Accessible.description: isEnglishUi
                            ? "Anime card. Press Enter to open details."
                            : "Scheda anime. Premi Invio per aprire i dettagli."
    Keys.onReturnPressed: appController.selectAnime(animeData.id)
    Keys.onEnterPressed: appController.selectAnime(animeData.id)
    Keys.onSpacePressed: appController.selectAnime(animeData.id)
    
    function resolveCardCover(anime) {
        if (!anime || !anime.coverImage) {
            return ""
        }
        return anime.coverImage.extraLarge || anime.coverImage.large || anime.coverImage.medium || ""
    }
    
    // Supports both model roles and direct property (for flexibility)
    property var animeData: model.media || modelData.media
    property int progress: model.progress !== undefined ? model.progress : (modelData ? modelData.progress : 0)
    property string displayTitle: model.display_title || (modelData ? modelData.display_title : "Unknown")
    property string airingTime: model.airing_time_formatted || (modelData ? modelData.airing_time_formatted : "TBA")
    property bool isToday: model.is_today !== undefined ? model.is_today : (modelData ? modelData.is_today : false)
    
    Rectangle {
        id: cardContainer
        anchors.fill: parent
        anchors.margins: 10
        color: "#1f2937"
        radius: 12
        clip: true
        
        // Border/Shadow hover effect
        border.color: (mouseArea.containsMouse || root.activeFocus) ? "#3b82f6" : "#374151"
        border.width: (mouseArea.containsMouse || root.activeFocus) ? 2 : 1
        
        // Hover Scale Animation
        scale: mouseArea.containsMouse ? 1.05 : 1.0
        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }
        Behavior on border.color { ColorAnimation { duration: 200 } }

        ColumnLayout {
            anchors.fill: parent
            spacing: 0
            
            // Cover Image
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 200
                color: "#111827"
                clip: true
                
                // Skeleton Loader
                Rectangle {
                    anchors.fill: parent
                    color: "#1f2937"
                    visible: coverImage.status !== Image.Ready
                    
                    Rectangle {
                        width: parent.width * 2
                        height: parent.height
                        x: -parent.width
                        opacity: 0.1
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.5; color: "white" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                        
                        NumberAnimation on x {
                            from: -parent.width; to: parent.width; duration: 1500; loops: Animation.Infinite
                            running: parent.visible
                        }
                    }
                }

                Image {
                    id: coverImage
                    anchors.fill: parent
                    source: root.resolveCardCover(animeData)
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    sourceSize.width: Math.max(1, Math.round(width))
                    sourceSize.height: Math.max(1, Math.round(height))
                    opacity: status === Image.Ready ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 300 } }
                }
                
                // Progress Badge
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 8
                    width: 60
                    height: 24
                    color: "#3b82f6"
                    radius: 4
                    z: 5
                    
                    Text {
                        anchors.centerIn: parent
                        text: "Ep. " + progress
                        color: "white"
                        font.pixelSize: 11
                        font.bold: true
                    }
                }
                
                // Today Badge
                Rectangle {
                    visible: isToday
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: 8
                    width: 50
                    height: 20
                    color: "#ef4444" 
                    radius: 4
                    z: 5
                    
                    Text {
                        anchors.centerIn: parent
                        text: root.isEnglishUi ? "TODAY" : "OGGI"
                        color: "white"
                        font.pixelSize: 10
                        font.bold: true
                    }
                }
            }
            
            // Info Area
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: 12
                spacing: 4
                
                Text {
                    id: titleText
                    Layout.fillWidth: true
                    text: displayTitle
                    color: "white"
                    font.pixelSize: 13 
                    font.bold: true
                    wrapMode: Text.WordWrap
                    maximumLineCount: 4
                    elide: Text.ElideNone
                }
                
                Text {
                    Layout.fillWidth: true
                    text: animeData.nextAiringEpisode ? 
                          ((root.isEnglishUi ? "Next: Ep " : "Prossimo: Ep ") + animeData.nextAiringEpisode.episode + " • " + airingTime) :
                          (root.isEnglishUi ? "Finished or TBA" : "Terminato o TBA")
                    color: animeData.nextAiringEpisode ? "#34d399" : "#9ca3af"
                    font.pixelSize: 11
                    font.bold: !!animeData.nextAiringEpisode
                }
                
                Item { Layout.fillHeight: true }
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            
            // Subtle Ripple effect
            onPressed: cardContainer.opacity = 0.8
            onReleased: cardContainer.opacity = 1.0
            onCanceled: cardContainer.opacity = 1.0
            
            onClicked: {
                appController.selectAnime(animeData.id)
            }
        }
    }
}
