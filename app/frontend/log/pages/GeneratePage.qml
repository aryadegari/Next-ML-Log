import QtQuick
import QtQuick.Dialogs
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../../shared_controls"

Item {
    clip: true

    Rectangle {
        id: outline_of_options
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            bottom: save_section.top
            margins: theme_handler.page_loader_margins
        }
        color: theme_handler.background_colour
        radius: theme_handler.rectangle_radius
        border {
            color: theme_handler.secondary_bar_colour
            width: theme_handler.border_width
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: theme_handler.text_margins
            color: theme_handler.background_colour

            ColumnLayout {
                anchors.fill: parent
                RowLayout {
                    ToggleButton {
                        button_description: qsTr("Save Original")
                        checked: persistent_settings.check_save_original
                        onClicked: {
                            persistent_settings.check_save_original = !persistent_settings.check_save_original
                            save_original_file = this.checked
                        }
                    }
                }
                // Fill up the rest of the space
                RowLayout {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
        }
    }

    Rectangle {
        id: save_section
        anchors {
            bottom: parent.bottom
            left: parent.left
            right: parent.right
            leftMargin: theme_handler.page_loader_margins
            rightMargin: theme_handler.page_loader_margins
            bottomMargin: theme_handler.page_loader_margins
        }
        height: theme_handler.upload_area_height
        color: theme_handler.background_colour

        Uploader {
            placeholder: qsTr("Choose destination to save file")
            currently_loaded_file: current_output_file_destination
            file_dialog_title: qsTr("Choose where to save the output")
            file_dialog_filters: ["CSV files (*.csv)"]
            button_one_text: qsTr("Choose")
            button_two_text: qsTr("Create")
            file_dialog.onAccepted: {
                change_opening_folder_accordingly()
                currently_loaded_file = file_dialog.currentFile.toString().slice("file:///".length)
                current_output_file_destination = currently_loaded_file // Update global variable.
            }
            // Unique set up for this page
            file_dialog.fileMode: FileDialog.SaveFile
            button_two.onClicked: {
                loading_bar.open()
                backend.generate_log_files(current_output_file_destination, save_original_file)
            }
            button_two.enabled: current_output_file_destination !== qsTr("")
        }
    }
}
