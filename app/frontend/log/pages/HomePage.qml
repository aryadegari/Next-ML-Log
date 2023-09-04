import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform
import "../../shared_controls"

Item {
    clip: true

    function reset_with_new_bpmn_and_mxml_files() {
        parse_successful = false
        has_tried_to_parse = false
        if ((currently_loaded_bpmn_file !== qsTr("")) && (currently_loaded_mxml_file !== qsTr(""))) {
            loading_bar.open()
            var bpmn_file = currently_loaded_bpmn_file
            var mxml_file = currently_loaded_mxml_file
            backend.update_process_model_with_mxml_and_bpmn_files(bpmn_file, mxml_file)
        }
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
                bottom: bpmn_upload_area.top
                bottomMargin: theme_handler.page_loader_margins
            }
            source: persistent_settings.use_light_theme_on_startup ? "../../assets/next_log_light.png" : "../../assets/next_log_dark.png"
            fillMode: Image.Pad
        }

        Rectangle {
            id: bpmn_upload_area
            anchors {
                left: parent.left
                right: parent.right
                bottom: mxml_upload_area.top
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            height: theme_handler.upload_area_height
            color: theme_handler.background_colour

            Uploader {
                id: bpmn_uploader
                placeholder: qsTr("Select a BPMN file to upload")
                currently_loaded_file: currently_loaded_bpmn_file
                file_dialog_title: qsTr("Select a BPMN file to load")
                file_dialog_filters: ["BPMN files (*.bpmn *.xml)"]
                button_two_link: qsTr("https://demo.bpmn.io/new")
                button_one_text: qsTr("Upload")
                button_two_text: qsTr("Create")
                file_dialog.onAccepted: {
                    change_opening_folder_accordingly()
                    currently_loaded_file = file_dialog.currentFile.toString().slice("file:///".length)
                    currently_loaded_bpmn_file = currently_loaded_file // Update global variable.
                    view_page.reloadWebEngineView()
                    backend.uploaded_new_bpmn_file(currently_loaded_file)
                    reset_with_new_bpmn_and_mxml_files()
                }
            }
        }

        Rectangle {
            id: mxml_upload_area
            anchors {
                left: parent.left
                right: parent.right
                bottom: reset_button.top
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            height: theme_handler.upload_area_height
            color: theme_handler.background_colour

            Uploader {
                id: mxml_uploader
                placeholder: qsTr("Select a MXML file to upload")
                currently_loaded_file: currently_loaded_mxml_file
                file_dialog_title: qsTr("Select a MXML file to load")
                file_dialog_filters: ["MXML files (*.mxml *.xml)"]
                button_two_link: qsTr("https://bimp.cs.ut.ee/simulator/")
                button_one_text: qsTr("Upload")
                button_two_text: qsTr("Create")
                file_dialog.onAccepted: {
                    change_opening_folder_accordingly()
                    currently_loaded_file = file_dialog.currentFile.toString().slice("file:///".length)
                    currently_loaded_mxml_file = currently_loaded_file // Update global variable.
                    reset_with_new_bpmn_and_mxml_files()
                }
            }
        }

        NormalButton {
            id: reset_button
            text: qsTr("Reset")
            anchors {
                left: parent.left
                right: parent.right
                bottom: parent.bottom
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            onClicked: {
                currently_loaded_bpmn_file = qsTr("")
                bpmn_uploader.currently_loaded_file = currently_loaded_bpmn_file
                currently_loaded_mxml_file = qsTr("")
                mxml_uploader.currently_loaded_file = currently_loaded_mxml_file
            }
        }
    }
}
