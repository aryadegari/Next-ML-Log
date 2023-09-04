import QtQuick
import QtQuick.Controls
import "../../shared_controls"

Item {
    property string labelText
    property string placeholder
    property alias textValue: parameter_input.text

    Rectangle {
        color: theme_handler.background_colour
        radius: theme_handler.rectangle_radius

        Text {
            id: parameter_label
            text: labelText
            color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
        }

        TextField {
            id: parameter_input
            anchors {
                left: parameter_label.right
                leftMargin: theme_handler.page_loader_margins
            }
            placeholderText: placeholder
            placeholderTextColor: theme_handler.secondary_text_colour
            color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
            background: Rectangle {
                color: theme_handler.background_colour
                radius: theme_handler.rectangle_radius
            }
        }
    }
    anchors {
        left: parent.left
        leftMargin: theme_handler.page_loader_margins
        rightMargin: theme_handler.page_loader_margins
        topMargin: theme_handler.page_loader_margins
    }
}
