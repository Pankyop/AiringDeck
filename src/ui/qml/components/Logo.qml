import QtQuick
import QtQuick.Layouts

Item {
    id: root
    width: 64
    height: 64
    implicitWidth: width
    implicitHeight: height
    
    property color primaryColor: "#34d399" // Teal
    property color secondaryColor: "#1e293b" // Slate
    property bool animated: true
    
    Rectangle {
        anchors.fill: parent
        radius: width * 0.2
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#2d3748" }
            GradientStop { position: 1.0; color: "#1a202c" }
        }
        
        GridLayout {
            anchors.fill: parent
            anchors.margins: parent.width * 0.15
            columns: 3
            rows: 3
            rowSpacing: parent.width * 0.05
            columnSpacing: parent.width * 0.05
            
            Repeater {
                model: 9
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: width * 0.3
                    
                    // Logic to form the 'Play' Triangle in a 3x3 grid:
                    // 0 1 2
                    // 3 4 5
                    // 6 7 8
                    // Triangle: 0, 3, 4, 6
                    
                    readonly property bool isTriangle: {
                        if (index === 0 || index === 3 || index === 4 || index === 6) return true;
                        return false;
                    }
                    
                    color: isTriangle ? root.primaryColor : "#334155"
                    opacity: isTriangle ? 1.0 : 0.4
                    scale: 1
                    
                    Behavior on scale {
                        enabled: root.animated
                        NumberAnimation { duration: 500; easing.type: Easing.OutBack }
                    }
                }
            }
        }
    }
}
