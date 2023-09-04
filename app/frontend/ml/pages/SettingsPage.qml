import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import "../../shared_controls"

Item {
    clip: true

    // Dyllan: Note; might not be consistent from OS to OS, should be weary. Works on Windows
    function get_folder_location() {
        var path = folder_dialog.folder.toString()
        path = path.replace(/^(file:\/{3})/, "") // removes "file:///"
        return path
    }

    // Dyllan: Lol super hacky
    function get_font_size_for_directory_text() {
        if (default_folder_text.text.length < 40)
            return theme_handler.font_text_size
        if (default_folder_text.text.length < 60)
            return theme_handler.font_text_size - 2
        if (default_folder_text.text.length <= 95)
            return theme_handler.font_text_size - 4
        return theme_handler.font_text_size - 6
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        ColumnLayout {
            id: column_layout
            anchors {
                left: parent.left
                right: parent.right
            }
            // Actual Setting Options;
            RowLayout {
                ToggleButton {
                    button_description: qsTr("Open ML.log in Fullscreen Mode on Startup?")
                    checked: persistent_settings.open_window_as_maximised_on_startup
                    onClicked: {
                        persistent_settings.open_window_as_maximised_on_startup
                                = !persistent_settings.open_window_as_maximised_on_startup
                    }
                }
            }
            RowLayout {
                ToggleButton {
                    button_description: qsTr("Use Dark Theme?")
                    checked: !persistent_settings.use_light_theme_on_startup
                    onClicked: {
                        theme_handler.invert_theme()
                    }
                }
            }

            RowLayout {
                ToggleButton {
                    button_description: qsTr("Use >_next(log) csv?")
                    checked: persistent_settings.use_next_log_csv
                    onClicked: persistent_settings.use_next_log_csv = !persistent_settings.use_next_log_csv
                }
            }

            RowLayout {
                ToggleButton {
                    button_description: qsTr("Use Default Folder Directory?")
                    checked: persistent_settings.use_default_folder_directory
                    onClicked: persistent_settings.use_default_folder_directory = !persistent_settings.use_default_folder_directory
                }
            }

            // Folder Dialog
            RowLayout {
                FolderDialog {
                    id: folder_dialog
                    folder: persistent_settings.default_folder_location
                    onAccepted: {
                        persistent_settings.default_folder_location = folder_dialog.currentFolder
                    }
                }

                Text {
                    id: default_folder_text
                    text: " --> " + get_folder_location()
                    font {
                        pointSize: get_font_size_for_directory_text()
                        family: theme_handler.font_family
                    }
                    color: theme_handler.primary_text_colour
                    Layout.fillWidth: true
                }

                NormalButton {
                    id: choose_folder_button
                    text: qsTr("Choose")
                    onClicked: folder_dialog.open()
                }
            }
            // Licensing
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Text {
                    text: qsTr("<br>Licensing:<br>")
                    font {
                        pointSize: theme_handler.font_text_size
                        family: theme_handler.font_family
                    }
                    color: theme_handler.secondary_text_colour
                }
            }
            RowLayout {
                Text {
                    text: qsTr("Copyright (C) 2023, Dyllan Cartwright & Radu Sterie & Arash Yadegari.<br><br>
This program is free software: you can redistribute it and/or modify it under the terms of
the GNU General Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.<br><br>
Likewise, this project was created with open souce tools available from Qt and BPMN.iO, therefore this
software can be used for studies or non-commercial projects - go to https://www.qt.io and https://bpmn.io/
for more information.")
                    font {
                        pointSize: theme_handler.font_text_size
                        family: theme_handler.font_family
                    }
                    color: theme_handler.secondary_text_colour
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
