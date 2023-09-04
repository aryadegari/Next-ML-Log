import QtQuick
import QtQuick.Controls.Basic


Button {
    id: button
    height: theme_handler.left_bar_button_height
    width: theme_handler.left_bar_button_width
    icon {
        source: icon_source
        color: get_icon_colour()
        height: parent.height / 2
        width: parent.width / 2
    }

    property url icon_source
    property bool is_active_page

    function get_icon_colour() {
        if (button.down || button.hovered) return theme_handler.alt_icon_colour
        else return theme_handler.primary_text_colour
    }

    function get_button_colour() {
        if (!button.enabled) return theme_handler.disabled_red_colour
        if (button.down) return theme_handler.left_bar_button_clicked_colour
        else if (button.hovered) return theme_handler.left_bar_button_hovered_colour
        else return theme_handler.left_bar_button_bg_colour
    }

    background: Rectangle {
        anchors.fill: parent
        color: get_button_colour()
        opacity: button.enabled ? 1 : 0.35
        //Left Hover/Clicked highight
        Rectangle {
            anchors {
                top: parent.top
                left: parent.left
                bottom: parent.bottom
            }
            color: theme_handler.left_bar_button_edge_colour
            width: theme_handler.left_bar_button_edge_width
            visible: is_active_page
        }
    }

    HoverHandler {
        acceptedDevices: PointerDevice.Mouse
        cursorShape: Qt.PointingHandCursor
    }
}
