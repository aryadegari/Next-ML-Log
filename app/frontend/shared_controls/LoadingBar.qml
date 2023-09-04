import QtQuick
import QtQuick.Controls.Basic

Popup {
    anchors.centerIn: Overlay.overlay
    closePolicy: Popup.NoAutoClose
    modal: true

    background: Rectangle {
        anchors.fill: parent
        color: theme_handler.is_currently_light_theme ? theme_handler.primary_text_colour : theme_handler.primary_bar_colour
    }

    BusyIndicator {
        palette.dark: theme_handler.is_currently_light_theme ? theme_handler.primary_bar_colour : theme_handler.primary_text_colour
        running: true
    }
}
