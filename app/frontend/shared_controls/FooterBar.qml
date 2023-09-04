import QtQuick

Rectangle {
    anchors {
        left: left_bar.right
        right: parent.right
        bottom: parent.bottom
    }
    height: theme_handler.footer_bar_height
    color: theme_handler.secondary_bar_colour
    Text {
        text: qsTr("Authors: Dyllan Cartwright & Radu Sterie & Arash Yadegari | Rijksuniversiteit Groningen | " + main_window.version_number)
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        font.pointSize: theme_handler.font_topbar_and_footerbar_size
        font.family: theme_handler.font_family
        color: theme_handler.secondary_text_colour
    }
}
