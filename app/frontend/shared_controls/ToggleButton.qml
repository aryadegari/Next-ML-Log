import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SwitchDelegate {
    id: control
    Layout.fillWidth: true
    property string button_description

    contentItem: Text {
        rightPadding: control.indicator.width + control.spacing
        text: button_description
        font.family: theme_handler.font_family
        font.pointSize: theme_handler.font_text_size
        opacity: enabled ? 1.0 : 0.3
        color: theme_handler.primary_text_colour
        elide: Text.ElideRight
        verticalAlignment: Text.AlignVCenter
    }

    indicator: Rectangle {
        implicitWidth: 48
        implicitHeight: 26
        x: control.width - width - control.rightPadding
        y: parent.height / 2 - height / 2
        radius: 13
        color: control.checked ? theme_handler.enabled_green_colour : theme_handler.disabled_red_colour
        border.color: control.checked ? theme_handler.primary_bar_colour : theme_handler.secondary_bar_colour

        Rectangle {
            x: control.checked ? parent.width - width : 0
            width: 26
            height: 26
            radius: 13
            color: control.down ? theme_handler.secondary_bar_colour : theme_handler.primary_bar_colour
            border.color: control.checked ? (control.down ? "#17a81a" : "#21be2b") : "#999999"
        }
    }

    background: Rectangle {
        implicitWidth: 100
        implicitHeight: 40
        visible: control.down || control.highlighted
        color: control.down ? theme_handler.secondary_bar_colour : theme_handler.background_colour
    }
}
