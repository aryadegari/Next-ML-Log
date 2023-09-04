import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform
import "../../shared_controls"

Item {
    clip: true

    function uploaded_new_file() {
        var file_path
        if (!persistent_settings.use_default_folder_directory) {
            // Update the file_dialog's opening folder to the current one
            file_path = file_dialog.currentFile.toString().slice("file://".length)
            var parts = file_path.split("/")
            parts.pop()
            file_dialog.folder = "file://" + parts.join("/")
        } else
            file_dialog.folder = persistent_settings.default_folder_location
        file_path = file_dialog.currentFile.toString().slice("file:///".length)
        current_loaded_file_path = file_path // Update global variable.
        backend.uploaded_new_file(file_path)
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        Image {
            id: logo_pic
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                bottom: upload_area.top
                bottomMargin: theme_handler.page_loader_margins
            }
            source: persistent_settings.use_light_theme_on_startup ? "../../assets/ai_log_light.png" : "../../assets/ai_log_dark.png"
            fillMode: Image.Pad
        }

        Rectangle {
            id: upload_area
            anchors {
                left: parent.left
                right: parent.right
                bottom: parent.bottom
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            height: theme_handler.upload_area_height
            color: theme_handler.background_colour

            Rectangle {
                id: file_path_area
                anchors {
                    top: upload_area.top
                    left: upload_area.left
                    bottom: upload_area.bottom
                    right: upload_button.left
                    rightMargin: theme_handler.page_loader_margins
                }
                color: theme_handler.background_colour
                radius: theme_handler.rectangle_radius
                border {
                    color: theme_handler.secondary_bar_colour
                    width: theme_handler.border_width
                }
                
                TextField {
                    id: file_path_text
                    readOnly: true
                    anchors {
                        left: file_path_area.left
                        leftMargin: 5
                        right: file_path_area.right
                        rightMargin: 5
                        verticalCenter: file_path_area.verticalCenter
                    }
                    color: theme_handler.primary_text_colour
                    text: current_loaded_file_path
                    placeholderText: qsTr("Select a .csv file to upload")
                    placeholderTextColor: theme_handler.secondary_text_colour
                    font {
                        family: theme_handler.font_family
                        pointSize: theme_handler.font_text_size
                        italic: true
                    }
                    background: Rectangle {
                        color: theme_handler.background_colour
                    }
                }
            }

            FileDialog {
                id: file_dialog
                title: "Select a .csv / .mxml file to load"
                nameFilters: [".csv files (*.csv)", ".mxml files (*.mxml *.xml *.txt)"]
                folder: persistent_settings.default_folder_location
                onAccepted: uploaded_new_file()
            }

            NormalButton {
                id: upload_button
                text: "Load"
                anchors {
                    top: upload_area.top
                    bottom: upload_area.bottom
                    right: upload_area.right
                    rightMargin: theme_handler.page_loader_margins
                }
                onClicked: file_dialog.open()
            }
        }
    }
}
