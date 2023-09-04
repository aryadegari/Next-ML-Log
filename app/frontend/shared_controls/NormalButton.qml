import QtQuick
import QtQuick.Controls.Basic

Button {
    id: normal_button
    width: theme_handler.normal_button_width
    text: qsTr("Button")

    function get_button_text_colour() {
        if (normal_button.down || normal_button.hovered) return theme_handler.hover_button_text_colour
        else return theme_handler.primary_text_colour
    }

    contentItem: Text {
        text: normal_button.text
        font.family: theme_handler.font_family
        font.pointSize: theme_handler.font_text_size
        color: get_button_text_colour()
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    background: Rectangle {
        anchors.fill: normal_button
        color: normal_button.enabled ? theme_handler.secondary_bar_colour : theme_handler.disabled_red_colour
        radius: theme_handler.rectangle_radius
    }
}
