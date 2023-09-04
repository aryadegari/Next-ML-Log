import QtQuick
import QtQuick.Controls
import "../../shared_controls"
import QtQuick.Layouts

Item {
    property alias list_model: model
    property var parameters: ({})
    anchors.fill: parent

    Text {
        id: results_parameters_header
        text: JSON.stringify(parameters) === "{\"\":\"\"}" ? "" : "Parameters"
        font.bold: true
        color: theme_handler.primary_text_colour
    }

    Component {
        id: delegate

        Item {
            id: item
            width: 200
            height: 25

            Row {
                anchors.fill: parent
                anchors.leftMargin: theme_handler.page_loader_margins + 75
                spacing: 20

                Text {
                    text: parameter_name
                    color: theme_handler.primary_text_colour
                }

                Text {
                    text: parameter_value
                    color: theme_handler.primary_text_colour
                }
            }
        }
    }

    ListModel {
        id: model
        Component.onCompleted: {
            for (var key of Object.keys(parameters)) {
                if (parameters[key] == null) {
                    this.append(createListElement(key, ""))
                }
                else{
                    this.append(createListElement(key, parameters[key]))
                }
            }
        }
        function createListElement(key, value) {
            return {
                "parameter_name": key,
                "parameter_value": value.toString()
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
