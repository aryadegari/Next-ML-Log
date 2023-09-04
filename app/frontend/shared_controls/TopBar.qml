import QtQuick
import QtQuick.Controls

Rectangle {
    id: top_bar
    property string app_title: qsTr("Synthetic Event Log Generation Tool")
    anchors {
        top: parent.top
        left: parent.left
        leftMargin: theme_handler.left_bar_width
        right: parent.right
        rightMargin: 15
    }
    height: theme_handler.top_bar_height
    color: theme_handler.primary_bar_colour

    MouseArea {
        id: title_mouse_area
        anchors.fill: parent

        onDoubleClicked: {
            if (is_window_maximised) {
                main_window.showNormal()
                is_window_maximised = false
            } else {
                main_window.showMaximized()
                is_window_maximised = true
            }
        }

        DragHandler {
            id: resize_handler
            onActiveChanged: if (active) main_window.startSystemMove()
            onActiveTranslationChanged: is_window_maximised = false // When you start dragging, Qt goes to "Normal"
        }
    }

    Label {
        id: title_bar_label
        anchors.verticalCenter: top_bar.verticalCenter
        anchors.horizontalCenter: top_bar.horizontalCenter
        text: app_title
        font.pointSize: theme_handler.font_topbar_and_footerbar_size
        font.family: theme_handler.font_family
        color: theme_handler.primary_text_colour
    }

    Rectangle {
        anchors {
            top: top_bar.top
            bottom: top_bar.bottom
            right: top_bar.right
            left: title_bar_label.right
        }

        TitleBar {
            id: title_bar_buttons
        }
    }
}
