import QtQuick

Item {
    anchors.fill: parent
    MouseArea {
        width: 25
        height: 25
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        cursorShape: Qt.SizeAllCursor
        acceptedButtons: Qt.LeftButton
        pressAndHoldInterval: 50
        onPressAndHold: main_window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
    }
}
