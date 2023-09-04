import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform
import "../../shared_controls"

Item {
    clip: true

    readonly property string default_text: qsTr("Click 'Parse Rules' to see if rules are accepted.\nClick 'Available' to see all defined events and attributes.")
    property string output_text: default_text

    function change_opening_folder_accordingly() {
        var file_path
        if (!persistent_settings.use_default_folder_directory) {
            // Update the file_dialog's opening folder to the current one
            file_path = file_dialog_load.currentFile.toString().slice("file://".length)
            var parts = file_path.split("/")
            parts.pop()
            file_dialog_load.folder = "file://" + parts.join("/")
        } else
            file_dialog_load.folder = persistent_settings.default_folder_location
    }

    function get_colour() {
        if (!has_tried_to_parse)
            return theme_handler.background_colour
        if (!parse_successful)
            return theme_handler.disabled_red_colour
        return theme_handler.enabled_green_colour
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        Rectangle {
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                bottom: button_area.top
            }
            radius: theme_handler.rectangle_radius
            color: theme_handler.rules_background_colour
            border {
                color: theme_handler.secondary_bar_colour
                width: theme_handler.border_width
            }
            ScrollView {
                anchors.fill: parent
                anchors.margins: theme_handler.text_margins
                TextArea {
                    id: rule_defs
                    text: persistent_settings.last_rules_text
                    color: theme_handler.primary_text_colour
                    font {
                        // weight: Font.DemiBold
                        styleName: theme_handler.font_family
                        pointSize: theme_handler.rules_font_size
                    }
                    onTextChanged: {
                        has_tried_to_parse = false
                        parse_successful = false
                        output_text = default_text
                        persistent_settings.last_rules_text = rule_defs.text
                    }
                }
            }
        }

        Rectangle {
            id: button_area
            anchors {
                bottom: output_area.top
                left: parent.left
                right: parent.right
            }
            color: theme_handler.background_colour
            height: theme_handler.upload_area_height + 2 * theme_handler.page_loader_margins

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: theme_handler.page_loader_margins
                anchors.rightMargin: theme_handler.page_loader_margins

                FileDialog {
                    id: file_dialog_load
                    title: qsTr("Choose Rules")
                    nameFilters: ["Rule files (*.rules)"]
                    folder: persistent_settings.default_folder_location
                    onAccepted: {
                        change_opening_folder_accordingly()
                        var rule_file_path = file_dialog_load.currentFile.toString().slice("file:///".length)
                        var rules_as_text = backend.read_loaded_rules(rule_file_path)
                        rule_defs.text = rules_as_text
                    }
                }

                NormalButton {
                    text: qsTr("Load Rules")
                    Layout.fillWidth: true
                    onClicked: file_dialog_load.open()
                }

                FileDialog {
                    id: file_dialog_save
                    title: qsTr("Choose where to save Rules")
                    nameFilters: ["Rule files (*.rules)"]
                    folder: persistent_settings.default_folder_location
                    fileMode: FileDialog.SaveFile
                    onAccepted: {
                        change_opening_folder_accordingly()
                        var rule_file_path = file_dialog_save.currentFile.toString().slice("file:///".length)
                        backend.save_rules(rule_defs.text, rule_file_path)
                    }
                }

                NormalButton {
                    Layout.fillWidth: true
                    text: qsTr("Save Rules")
                    onClicked: {
                        file_dialog_save.open()
                    }
                }
                NormalButton {
                    Layout.fillWidth: true
                    text: qsTr("Parse Rules")
                    onClicked: {
                        has_tried_to_parse = true
                        var response = backend.parse_rules(rule_defs.text)
                        parse_successful = response === qsTr("Accepted!")
                        output_text = response
                    }
                }
                NormalButton {
                    Layout.fillWidth: true
                    text: qsTr("Available")
                    onClicked: {
                        parse_successful = false // just to be safe lol
                        has_tried_to_parse = false
                        output_text = backend.get_attributes_and_event_names()
                    }
                }
            }
        }

        Rectangle {
            id: output_area
            anchors {
                bottom: parent.bottom
                left: parent.left
                right: parent.right
                bottomMargin: theme_handler.page_loader_margins
            }
            color: get_colour()
            radius: theme_handler.rectangle_radius
            height: theme_handler.upload_area_height + 2 * theme_handler.page_loader_margins

            ScrollView {
                anchors.fill: output_area
                anchors.margins: theme_handler.text_margins
                TextEdit {
                    readOnly: true
                    color: has_tried_to_parse ? theme_handler.primary_text_colour : theme_handler.secondary_text_colour
                    text: output_text
                    font {
                        styleName: theme_handler.font_family
                        pointSize: theme_handler.rules_font_size
                    }
                }
            }
        }
    }
}
