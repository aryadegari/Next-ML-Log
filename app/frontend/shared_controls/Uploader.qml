import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform


Item {
    anchors.fill: parent

    property string placeholder: qsTr("")
    property string currently_loaded_file: qsTr("")
    property string file_dialog_title: qsTr("")
    property var file_dialog_filters: [""]
    property string button_two_link: qsTr("")
    property string button_one_text: qsTr("")
    property string button_two_text: qsTr("")
    property alias file_dialog: file_dialog
    property alias button_one: button_one
    property alias button_two: button_two

    function change_opening_folder_accordingly() {
        var file_path
        if (!persistent_settings.use_default_folder_directory) {
            // Update the file_dialog's opening folder to the current one
            file_path = file_dialog.currentFile.toString().slice("file://".length)
            var parts = file_path.split("/")
            parts.pop()
            file_dialog.folder = "file://" + parts.join("/")
        } else
            file_dialog.folder = persistent_settings.default_folder_location
    }

    Rectangle {
        id: file_path_area
        anchors {
            top: parent.top
            bottom: parent.bottom
            left: parent.left
            right: button_area.left
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
            text: currently_loaded_file
            placeholderText: placeholder
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

    Rectangle {
        id: button_area
        width: 2 * theme_handler.normal_button_width + theme_handler.page_loader_margins
        anchors {
            top: parent.top
            bottom: parent.bottom
            right: parent.right
        }
        color: theme_handler.background_colour

        FileDialog {
            id: file_dialog
            title: file_dialog_title
            nameFilters: file_dialog_filters
            folder: persistent_settings.default_folder_location
        }

        NormalButton {
            id: button_one
            text: button_one_text
            anchors {
                top: button_area.top
                bottom: button_area.bottom
                right: button_two.left
                rightMargin: theme_handler.page_loader_margins
            }
            onClicked: file_dialog.open()
        }

        NormalButton {
            id: button_two
            text: button_two_text
            anchors {
                top: button_area.top
                bottom: button_area.bottom
                right: button_area.right
            }
            onClicked: Qt.openUrlExternally(button_two_link)
        }
    }
}
