import QtQuick
import QtQuick.Controls.Basic


Button {
    id: button
    property url icon_source

    icon {
        source: icon_source
        color: get_icon_colour()
    }
    background: Rectangle { color: get_button_colour() }

    function get_icon_colour() {
        if (button.down || button.hovered) return theme_handler.alt_icon_colour
        else return theme_handler.primary_text_colour
    }

    function get_button_colour() {
        if (button.down) {
            return theme_handler.left_bar_button_clicked_colour
        } else if (button.hovered) {
            return theme_handler.left_bar_button_hovered_colour
        } else {
            return theme_handler.left_bar_button_bg_colour
        }
    }

    HoverHandler {
        acceptedDevices: PointerDevice.Mouse
        cursorShape: Qt.PointingHandCursor
    }
}
