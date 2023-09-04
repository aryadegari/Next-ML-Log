import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform
import QtQuick.Layouts
import "../../shared_controls"
import "../components"

Item {
    clip: true

    function get_parameters() {
        return JSON.stringify(ml_log.training_parameters)
    }

    function reset_results() {
        parameters_loader.sourceComponent = null
        parameters_loader.sourceComponent = results_parameters
        image_loader.sourceComponent = null
        image_loader.sourceComponent = image_component
        fullscreen_image_loader.sourceComponent = null
        fullscreen_image_loader.sourceComponent = image_component
        train_test_stats_loader.sourceComponent = null
        train_test_stats_loader.sourceComponent = train_test_stats_component
    }

    property var training_information: {
        "train": "",
        "test": "",
        "model_name": ""
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        Window {
            id: fullscreen_window_image
            visible: false
            color: theme_handler.background_colour
            title: qsTr("ML.log")

            Loader {
                id: fullscreen_image_loader
                z: 1
                anchors.fill: parent
                sourceComponent: null
            }
        }

        LeftBarButton {
            id: fullscreen_image_button
            z: 2
            height: 35
            width: 35
            visible: image_loader.sourceComponent ? true : false
            anchors {
                top: image_loader.top
                left: image_loader.left
            }
            icon_source: "../../assets/maximise.png"
            background: Rectangle {
                anchors.fill: parent
                color: "transparent"
            }
            onClicked: fullscreen_window_image.showMaximized()
            
        }

        LeftBarButton {
            id: save_image_button
            z: 2
            height: 35
            width: 35
            visible: image_loader.sourceComponent ? true : false
            anchors {
                top: fullscreen_image_button.bottom
                left: image_loader.left
            }
            icon_source: "../../assets/floppy-disk.png"
            background: Rectangle {
                anchors.fill: parent
                color: "transparent"
            }
            onClicked: save_image_dialog.open()
        }

        LeftBarButton {
            id: next_image_button
            z: 2
            height: 35
            width: 35
            visible: image_loader.sourceComponent ? ((training_information["model_name"] === "Random Forest"
                                                      || training_information["model_name"] === "Generalized LVQ"
                                                      || training_information["model_name"] === "K-Nearest Neighbors")
                                                     ? true : false) : false
            anchors {
                top: save_image_button.bottom
                left: image_loader.left
            }
            icon_source: "../../assets/next.png"
            background: Rectangle {
                anchors.fill: parent
                color: "transparent"
            }
            onClicked: {
                backend.next_image()
                reset_results()
            }
        }

        LeftBarButton {
            id: previous_image_button
            z: 2
            height: 35
            width: 35
            visible: image_loader.sourceComponent ? ((training_information["model_name"] === "Random Forest"
                                                      || training_information["model_name"] === "Generalized LVQ"
                                                      || training_information["model_name"]
                                                      === "K-Nearest Neighbors") ? true : false) : false
            anchors {
                top: next_image_button.bottom
                left: image_loader.left
            }
            icon_source: "../../assets/previous.png"
            background: Rectangle {
                anchors.fill: parent
                color: "transparent"
            }
            onClicked: {
                backend.previous_image()
                reset_results()
            }
        }

        FileDialog {
            id: save_image_dialog
            title: "Save"
            nameFilters: [".png files (*.png)"]
            folder: persistent_settings.default_folder_location
            acceptLabel: "Save"
            fileMode: FileDialog.SaveFile
            property var save_file_path: null
            onAccepted: {
                var save_path = this.currentFile.toString().slice("file:///".length)
                this.save_file_path = save_path
                backend.save_model_image(this.save_file_path)
            }
        }

        Loader {
            id: image_loader
            z: 1
            anchors {
                right: parent.horizontalCenter
                left: parent.left
                top: parent.top
                bottom: upload_area.top
                bottomMargin: theme_handler.page_loader_margins
            }
            sourceComponent: null
        }

        Component {
            id: image_component
            FlickableImage {}
        }

        Loader {
            id: train_test_stats_loader
            z: 1
            anchors {
                left: parent.horizontalCenter
                right: parent.right
                top: parent.top
                bottom: parent.verticalCenter
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
            }
            sourceComponent: null
        }

        Component {
            id: train_test_stats_component
            Rectangle {
                color: theme_handler.background_colour

                anchors.fill: parent

                GridLayout {
                    id: grid
                    columns: 2
                    anchors.fill: parent
                    anchors.leftMargin: theme_handler.page_loader_margins
                    columnSpacing: theme_handler.page_loader_margins - 75
                    rowSpacing: theme_handler.page_loader_margins - 225

                    Text {
                        text: "<b>Train</b> " + training_information["train"] + (training_information["train"] === "" ? "" : "%")
                        color: theme_handler.primary_text_colour
                    }

                    Text {
                        text: "<b>Test</b> " + training_information["test"] + (training_information["test"] === "" ? "" : "%")
                        color: theme_handler.primary_text_colour
                    }

                    Text {
                        text: "<b>Accuracy</b>: " + ml_log.train_statistics["training_accuracy"]
                        color: theme_handler.primary_text_colour
                    }

                    Text {
                        text: "<b>Accuracy</b>: " + ml_log.train_statistics["testing_accuracy"]
                        color: theme_handler.primary_text_colour
                    }

                    Text {}

                    Text {}

                    Text {}

                    Text {}

                    Text {}

                    Text {}

                    Text {
                        text: "<b>f1</b>: " + ml_log.train_statistics["f1"]
                        color: theme_handler.primary_text_colour
                    }

                    Text {}

                    Text {
                        text: "<b>Precision</b>: " + ml_log.train_statistics["precision"]
                        color: theme_handler.primary_text_colour
                    }

                    Text {}

                    Text {
                        text: "<b>Recall</b>: " + ml_log.train_statistics["recall"]
                        color: theme_handler.primary_text_colour
                    }

                    Text {}
                }
            }
        }

        Loader {
            id: parameters_loader
            anchors {
                left: parent.horizontalCenter
                right: parent.right
                top: train_test_stats_loader.bottom
                bottom: upload_area.top
                leftMargin: theme_handler.page_loader_margins * 2
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            sourceComponent: results_parameters
        }

        Component {
            id: results_parameters
            Rectangle {
                color: theme_handler.background_colour

                ParameterTrainingList {
                    parameters: ml_log.training_parameters ? ml_log.training_parameters : {"": ""}
                }
            }
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
                    text: file_dialog.save_file_path
                    placeholderText: qsTr("Select a folder to save the model")
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
                title: "Save"
                nameFilters: [".pickle files (*.pickle)"]
                folder: persistent_settings.default_folder_location
                acceptLabel: "Save"
                fileMode: FileDialog.SaveFile
                property var save_file_path: null
                onAccepted: {
                    var save_path = this.currentFile.toString().slice("file://".length)
                    this.save_file_path = save_path
                    file_path_text.text = "Model saved on: " + save_path.slice(1)
                    backend.save_model(this.save_file_path)
                }
            }

            NormalButton {
                id: upload_button
                text: "Save"
                anchors {
                    top: upload_area.top
                    bottom: upload_area.bottom
                    right: upload_area.right
                    rightMargin: theme_handler.page_loader_margins
                }
                onClicked: {
                    if (select_model_page.is_training_completed == false) {
                        warning_dialog.warning_text = qsTr("No model to save.")
                        warning_dialog.open()
                        return
                    }
                    file_dialog.open()
                }
            }
        }
    }
}
