import QtQuick
import QtQuick.Controls.Basic
import "../../shared_controls"

Item {
    property alias list_model: model
    property var parameters: []
    anchors.fill: parent

    Component {
        id: delegate

        Item {
            id: item
            width: 200
            height: 50

            Row {
                anchors.fill: parent
                spacing: 75
                Text {
                    id: parameter_label
                    text: parameter_name
                    color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
                }

                TextField {
                    id: parameter_input
                    placeholderText: input_value ? input_value : parameters[param_index][1]
                    placeholderTextColor: theme_handler.secondary_text_colour
                    color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
                    background: Rectangle {
                        color: theme_handler.background_colour
                    }
                    onTextChanged: {
                        list_model.setProperty(index, "input_value", parameter_input.text)
                    }
                }
            }
        }
    }

    ListModel {
        id: model
        Component.onCompleted: {
            for (var i = 0; i < parameters.length; i++) {
                this.append(createListElement(i))
            }
        }

        function createListElement(i) {
            return {
                "parameter_name": parameters[i][0],
                "input_value": parameters[i][1],
                "param_index": i
            }
        }
    }

    ScrollView {
        id: scroll
        anchors.fill: parent
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff

        ListView {
            width: parent.width
            model: model
            delegate: delegate
        }
    }
}
