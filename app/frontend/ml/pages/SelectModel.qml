import QtQuick
import QtQuick.Controls.Basic
import "../../shared_controls"
import "../components"

Item {
    clip: true

    property var params_list_component: null
    property var features_to_plot_component: null
    property bool is_training_completed: false

    function parse_dictionary(string_dictionary) {
        return JSON.parse(main_window.all_ml_models)
    }    

    function parameters_dictionary_to_list(dictionary, selected_model) {
        var list = []
        for (var key in dictionary) {
            if (key === selected_model) {
                for (var key2 in dictionary[key]) {
                    var value = dictionary[key][key2]
                    list.push([key2, value])
                }
            }
        }
        return list
    }

    function create_features_input(){
        if (features_to_plot_component == null) {
            var component = Qt.createComponent("../components/FeaturesToPlotInput.qml")
            if (component.status === Component.Ready)
                finish_features_creation(component)
            else
                component.statusChanged.connect(finishCreation)
        }
    }

    function finish_features_creation(component) {
        if (component.status === Component.Ready) {
            features_to_plot_component = component.createObject(features_input_area)
            if (features_to_plot_component == null) {
                console.log("Error creating object")
            }
        } else if (component.status === Component.Error) {
            console.log("Error loading component:", component.errorString())
        }
    }

    function destroy_features_input() {
        if (features_to_plot_component !== null) {
            features_to_plot_component.destroy()
            features_to_plot_component = null
        }
    }

    function createParameterComponent() {
        if (params_list_component == null) {
            var component = Qt.createComponent("../components/ParameterInputList.qml")
            if (component.status === Component.Ready)
                finishCreation(component)
            else
                component.statusChanged.connect(finishCreation)
        }
    }

    function finishCreation(component) {
        if (component.status === Component.Ready) {
            params_list_component = component.createObject(select_parameters_area, {
                                                               "parameters": select_model_area.parameter_list
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

    function get_icon_colour() {
        if (auto_ml_button.down || auto_ml_button.hovered)
            return theme_handler.alt_icon_colour
        else
            return theme_handler.primary_text_colour
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        Rectangle {
            id: select_model_area
            property string selected_model_text: ""
            property var all_models_dictionary: parse_dictionary(main_window.all_ml_models)
            property var parameter_list: parameters_dictionary_to_list(select_model_area.all_models_dictionary,
                                                                       "Random Forest")

            anchors {
                left: parent.left
                right: parent.horizontalCenter
                top: parent.top
                bottom: parent.verticalCenter
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                topMargin: theme_handler.page_loader_margins
            }
            color: theme_handler.background_colour

            ListModel {
                id: select_model_list_model
            }

            Component.onCompleted: {
                for (var key in all_models_dictionary) {
                    select_model_list_model.append({
                        "btnText": key,
                        "selected": false
                    })
                }
            }

            ListView {
                anchors.fill: parent
                model: select_model_list_model
                delegate: NormalButton {
                    height: 80
                    width: parent.width
                    text: btnText
                    background: Rectangle {
                        color: selected ? theme_handler.secondary_bar_colour : "transparent"
                        radius: theme_handler.rectangle_radius
                    }
                    onClicked: {
                        destroy_features_input()
                        // Clear previous selections
                        for (var i = 0; i < select_model_list_model.count; i++) {
                            select_model_list_model.setProperty(i, "selected", false)
                        }
                        // Set the clicked item as selected
                        select_model_list_model.setProperty(index, "selected", true)
                        select_model_area.selected_model_text = select_model_list_model.get(index).btnText

                        select_model_area.parameter_list = parameters_dictionary_to_list(
                                    select_model_area.all_models_dictionary, select_model_area.selected_model_text)
                        
                        if (["K-Nearest Neighbors", "Generalized LVQ"].includes(select_model_area.selected_model_text)){
                            create_features_input()
                        }

                        destroyParameterComponent()
                        createParameterComponent()
                    }
                }
            }
        }

        Rectangle {
            id: select_parameters_area
            anchors {
                left: parent.horizontalCenter
                right: parent.right
                top: parent.top
                bottom: parent.verticalCenter
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                topMargin: theme_handler.page_loader_margins
            }
            color: theme_handler.background_colour
        }

        Rectangle {
            id: train_test_slider_area
            anchors {
                left: parent.left
                right: parent.right
                top: select_model_area.bottom
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                topMargin: theme_handler.page_loader_margins * 1.5
            }
            height: 50
            color: theme_handler.background_colour

            Slider {
                id: train_test_slider
                anchors.fill: parent
                from: 1
                to: 99
                value: 80
                stepSize: 1
            }

            Label {
                id: train_label
                text: qsTr("Train: ") + train_test_slider.value + "%" + " | " + qsTr(
                          "Test: ") + (100 - train_test_slider.value) + "%"
                font.bold: true
                color: persistent_settings.use_light_theme_on_startup ? "black" : "white"
            }
        }

        Rectangle {
            id: features_input_area
            anchors {
                left: train_button.right
                right: parent.right
                bottom: parent.bottom
                leftMargin: theme_handler.page_loader_margins
                rightMargin: theme_handler.page_loader_margins
                bottomMargin: theme_handler.page_loader_margins
            }
            color: theme_handler.background_colour
            height: parent.height / 4.5
        }

        LeftBarButton {
            id: auto_ml_button
            property bool selected: false
            width: theme_handler.left_bar_button_width + 5
            height: theme_handler.left_bar_button_height + 15
            anchors {
                bottom: parent.bottom
                left: parent.left
                bottomMargin: theme_handler.page_loader_margins - 30
                leftMargin: theme_handler.page_loader_margins - 30
            }
            Label {
                text: "AutoML"
                font.bold: true
                color: theme_handler.primary_text_colour
                horizontalAlignment: Text.AlignHCenter
            }
            background: Rectangle {
                color: auto_ml_button.selected ? theme_handler.secondary_bar_colour : "transparent"
                radius: theme_handler.rectangle_radius
            }
            icon_source: "../../assets/auto_ml.png"
            onClicked: {
                auto_ml_button.selected = !selected
                console.log(auto_ml_button.selected)
            }
        }

        NormalButton {
            id: train_button
            text: "Train"
            anchors {
                bottom: parent.bottom
                bottomMargin: theme_handler.page_loader_margins
                horizontalCenter: parent.horizontalCenter
            }

            onClicked: {
                if (auto_ml_button.selected == false) {
                    var parameters_dictionary = {}

                    if (features_to_plot_component) {
                        var all_features_to_plot = [features_to_plot_component.feature_1, features_to_plot_component.feature_2, features_to_plot_component.feature_3]
                        all_features_to_plot = all_features_to_plot.filter(item => item !== "")
                    }

                    if (params_list_component == null) {
                        warning_dialog.warning_text = qsTr("Please select a model.")
                        warning_dialog.open()
                        return
                    }

                    for (var i = 0; i < params_list_component.list_model.count; i++) {
                        parameters_dictionary[params_list_component.list_model.get(i).parameter_name] = params_list_component.list_model.get(i).input_value
                    }

                    var model_dictionary = {
                        "model": select_model_area.selected_model_text,
                        "parameters": parameters_dictionary,
                        "train_split": train_test_slider.value
                    }
                    
                    loading_bar.open()
                    //send data to backend
                    try {
                        if (select_model_area.selected_model_text == "Random Forest" || select_model_area.selected_model_text == "Decision Tree"){
                            all_features_to_plot = []
                        }
                        backend.get_data_from_view_and_train(JSON.stringify(model_dictionary),
                                                             theme_handler.background_colour,
                                                             persistent_settings.use_next_log_csv, all_features_to_plot)
                    } catch (e) {
                        console.error(e.message)
                        warning_dialog.warning_text = e.message
                        warning_dialog.open()
                        return
                    }

                } else {
                    loading_bar.open()
                    backend.perform_auto_ml(train_test_slider.value, theme_handler.background_colour,
                                           persistent_settings.use_next_log_csv)
                }
                results_page.training_information = {
                    "model_name": select_model_area.selected_model_text,
                    "train": train_test_slider.value,
                    "test": (100 - train_test_slider.value).toString()
                }
                is_training_completed = true
            }
        }
    }
}
