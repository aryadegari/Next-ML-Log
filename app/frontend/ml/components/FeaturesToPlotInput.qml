import QtQuick
import QtQuick.Controls.Basic
import "../../shared_controls"

Item{
    id: features_to_plot_item
    anchors.fill: parent
    property string feature_1: feature_input_1.text
    property string feature_2: feature_input_2.text 
    property string feature_3: feature_input_3.text

    Column {
        anchors.centerIn: parent
        spacing: 10

        TextField {
            id: feature_input_1
            placeholderText: "First feature to plot"
            placeholderTextColor: theme_handler.secondary_text_colour
            color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
            background: Rectangle {
                color: theme_handler.background_colour
            }
            anchors.horizontalCenter: parent.horizontalCenter
            verticalAlignment: TextInput.AlignVCenter
            onTextChanged: {
                feature_1 = feature_input_1.text
            }
        }

        TextField {
            id: feature_input_2
            placeholderText: "Second feature to plot"
            placeholderTextColor: theme_handler.secondary_text_colour
            color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
            anchors.horizontalCenter: parent.horizontalCenter
            verticalAlignment: TextInput.AlignVCenter
            background: Rectangle {
                color: theme_handler.background_colour
            }
            onTextChanged: {
                feature_1 = feature_input_1.text
            }
        }

        TextField {
            id: feature_input_3
            placeholderText: "Third feature to plot"
            placeholderTextColor: theme_handler.secondary_text_colour
            color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
            anchors.horizontalCenter: parent.horizontalCenter
            verticalAlignment: TextInput.AlignVCenter
            background: Rectangle {
                color: theme_handler.background_colour
            }
            onTextChanged: {
                feature_1 = feature_input_1.text
            }
        }
    }
}