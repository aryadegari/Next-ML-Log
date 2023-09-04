import QtQuick

Rectangle {
    property string header_text: qsTr("Home")
    height: theme_handler.header_height
    anchors {
        top: top_bar.bottom
        left: left_bar.right
        right: app_container.right
    }
    color: theme_handler.background_colour
    Text {
        text: header_text
        anchors {
            horizontalCenter: parent.horizontalCenter
            verticalCenter: parent.verticalCenter
        }
        font.family: theme_handler.font_family
        font.pointSize: theme_handler.font_page_title_size
        color: theme_handler.primary_text_colour
    }
}
