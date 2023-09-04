import QtQuick
import "../../shared_controls"
import "../components"
import QtQuick.Controls.Basic
import QtQuick.Dialogs
import Qt.labs.platform

Item {
    clip: true

    property var params_list_component: null
    property string pickle_file_path: ""
    property string data_file_path: ""
    property string default_active_pickled_image_path: "../../assets/active_pickled_image.png"

    function get_icon_colour() {
        if (test_button.down || test_button.hovered) return theme_handler.alt_icon_colour
        else return theme_handler.primary_text_colour
    }

    function createParameterComponent() {
        if (params_list_component == null) {
            var component = Qt.createComponent("../components/ParameterTrainingList.qml")
            if (component.status === Component.Ready)
                finishCreation(component)
            else
                component.statusChanged.connect(finishCreation)
        }
    }

    function finishCreation(component) {
        if (component.status === Component.Ready) {
            params_list_component = component.createObject(parameter_list_area, {
                                                               "parameters": ml_log.pretrained_model["parameters"]
                                                           })
            if (params_list_component == null) {
                console.log("Error creating object")
            }
        } else if (component.status === Component.Error) {
            console.log("Error loading component:", component.errorString())
        }
    }

    function destroyParameterComponent() {
        if (params_list_component !== null) {
            params_list_component.destroy()
            params_list_component = null
        }
    }

    function uploaded_new_pickle_file() {
        var file_path
        if (!persistent_settings.use_default_folder_directory) {
            file_path = file_dialog_pickle.currentFile.toString().slice("file://".length)
            var parts = file_path.split("/")
            parts.pop()
            file_dialog_pickle.folder = "file://" + parts.join("/")
        } else
            file_dialog_pickle.folder = persistent_settings.default_folder_location
        file_path = file_dialog_pickle.currentFile.toString().slice("file:///".length)
        pickle_file_path = file_path
        backend.uploaded_pretrained_model(pickle_file_path, theme_handler.background_colour)
        createParameterComponent()
        reload_image()
        accuracy.text = ""
        f1.text = ""
        precision.text = ""
        recall.text = ""
    }

    function uploaded_new_data_file() {
        var file_path
        if (!persistent_settings.use_default_folder_directory) {
            file_path = file_dialog_data.currentFile.toString().slice("file://".length)
            var parts = file_path.split("/")
            parts.pop()
            file_dialog_data.folder = "file://" + parts.join("/")
        } else
            file_dialog_data.folder = persistent_settings.default_folder_location
        file_path = file_dialog_data.currentFile.toString().slice("file:///".length)
        data_file_path = file_path
        backend.uploaded_validation_data(data_file_path)
    }

    function reload_image() {
        image_loader.sourceComponent = null
        image_loader.sourceComponent = image_component
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        Loader {
            id: image_loader
            z: 1
            anchors {
                right: parent.right
                left: parameter_list_area.right
                top: parent.top
                bottom: upload_area_data.top
                bottomMargin: theme_handler.page_loader_margins
            }
            sourceComponent: null
        }

        Component {
            id: image_component
            FlickableImage {
                image_source: default_active_pickled_image_path
            }
        }

        Rectangle {
            id: show_model_area
            color: theme_handler.background_colour
            anchors {

                top: parent.top
                left: parent.left
                right: parent.horizontalCenter
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
                topMargin: theme_handler.page_loader_margins
            }
            height: parent.height / 5

            Text {
                id: model_text
                text: "<b>Model:  </b>" + ml_log.pretrained_model["model"]
                color: theme_handler.primary_text_colour
            }

            Text {
                id: date_text
                anchors.top: model_text.bottom
                text: ml_log.pretrained_model["date"] === "" ? "" : "<b>Date:  </b>" + ml_log.pretrained_model["date"]
                color: theme_handler.primary_text_colour
            }

            Text {
                id: train_test_split
                anchors.top: date_text.bottom
                anchors.topMargin: theme_handler.page_loader_margins - 30
                text: ml_log.pretrained_model["train_size"]
                      === "" ? "" : "<b>Train</b> " + ml_log.pretrained_model["train_size"] + "\n"
                               + "<b>Test</b> " + (100 - ml_log.pretrained_model["train_size"])
                color: theme_handler.primary_text_colour
            }

            Text {
                id: accuracy
                anchors.top: train_test_split.bottom
                color: theme_handler.primary_text_colour
            }

            Text {
                id: f1
                anchors.top: accuracy.bottom
                color: theme_handler.primary_text_colour
            }

            Text {
                id: precision
                anchors.top: f1.bottom
                color: theme_handler.primary_text_colour
            }

            Text {
                id: recall
                anchors.top: precision.bottom
                color: theme_handler.primary_text_colour
            }
        }

        Rectangle {
            id: parameter_list_area
            color: theme_handler.background_colour
            anchors {
                bottom: upload_area_data.top
                left: parent.left
                right: parent.horizontalCenter
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            height: parent.height / 4
        }

        Rectangle {
            id: upload_area_data
            anchors {
                left: parent.left
                right: parent.right
                bottom: upload_area_pickle.top
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins - 25
            }
            height: theme_handler.upload_area_height
            color: theme_handler.background_colour

            Rectangle {
                id: file_path_area_data
                anchors {
                    top: upload_area_data.top
                    left: upload_area_data.left
                    bottom: upload_area_data.bottom
                    right: upload_button_data.left
                    rightMargin: theme_handler.page_loader_margins
                }
                color: theme_handler.background_colour
                radius: theme_handler.rectangle_radius
                border {
                    color: theme_handler.secondary_bar_colour
                    width: theme_handler.border_width
                }

                TextField {
                    id: file_path_text_data
                    readOnly: true
                    anchors {
                        left: file_path_area_data.left
                        leftMargin: 5
                        right: file_path_area_data.right
                        rightMargin: 5
                        verticalCenter: file_path_area_data.verticalCenter
                    }
                    color: theme_handler.primary_text_colour
                    text: data_file_path
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
                id: file_dialog_data
                title: "Select a .csv file to load"
                nameFilters: [".csv files (*.csv)"]
                folder: persistent_settings.default_folder_location
                onAccepted: uploaded_new_data_file()
            }

            NormalButton {
                id: upload_button_data
                text: "Load"
                anchors {
                    top: upload_area_data.top
                    bottom: upload_area_data.bottom
                    right: upload_area_data.right
                    rightMargin: theme_handler.page_loader_margins
                }
                onClicked: file_dialog_data.open()
            }
        }

        Rectangle {
            id: upload_area_pickle

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
                id: file_path_area_pickle
                anchors {
                    top: upload_area_pickle.top
                    left: upload_area_pickle.left
                    bottom: upload_area_pickle.bottom
                    right: upload_button_pickle.left
                    rightMargin: theme_handler.page_loader_margins
                }
                color: theme_handler.background_colour
                radius: theme_handler.rectangle_radius
                border {
                    color: theme_handler.secondary_bar_colour
                    width: theme_handler.border_width
                }
                
                TextField {
                    id: file_path_text_pickle
                    readOnly: true
                    anchors {
                        left: file_path_area_pickle.left
                        leftMargin: 5
                        right: file_path_area_pickle.right
                        rightMargin: 5
                        verticalCenter: file_path_area_pickle.verticalCenter
                    }
                    color: theme_handler.primary_text_colour
                    text: pickle_file_path
                    placeholderText: qsTr("Select a .pickle file to upload")
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
                id: file_dialog_pickle
                title: "Select a .pickle file to load"
                nameFilters: [".pickle files (*.pickle)"]
                folder: persistent_settings.default_folder_location
                onAccepted: {
                    destroyParameterComponent()
                    uploaded_new_pickle_file()
                }
            }

            NormalButton {
                id: upload_button_pickle
                text: "Load"
                anchors {
                    top: upload_area_pickle.top
                    bottom: upload_area_pickle.bottom
                    right: upload_area_pickle.right
                    rightMargin: theme_handler.page_loader_margins
                }
                onClicked: file_dialog_pickle.open()
            }
        }

        LeftBarButton {
            id: test_button
            hoverEnabled: true
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Test the loaded model with the given .csv file")
            anchors {
                top: upload_area_data.top
                bottom: upload_area_pickle.bottom
                right: parent.right
                left: upload_area_pickle.right
            }
            background: Rectangle {
                color:  theme_handler.secondary_bar_colour 
                radius: theme_handler.rectangle_radius
            }
            icon_source: "../../assets/test.png"
            onClicked: {
                if (pickle_file_path == "" || data_file_path == "") {
                    notification_no_files_loaded.open()
                    return
                }
                backend.test_pretrained_model_on_validation_data(persistent_settings.use_next_log_csv)
                accuracy.text = "<b>Accuracy:  </b>" + ml_log.pretrained_model["accuracy"]
                f1.text = "<b>f1:  </b>" + ml_log.pretrained_model["f1"]
                precision.text = "<b>Precision:  </b>" + ml_log.pretrained_model["precision"]
                recall.text = "<b>Recall:  </b>" + ml_log.pretrained_model["recall"]
            }
        }

        WarningDialog {
            id: notification_no_files_loaded
            warning_text: "Please load a .pickle file for the model \n and a .csv file for the training"
        }
    }
}
