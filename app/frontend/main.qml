import QtQml
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import "shared_controls"
import "log"
import "ml"

Window {
    id: main_window
    minimumWidth: 1250
    minimumHeight: 750
    visible: true
    flags: Qt.Window | Qt.FramelessWindowHint

    // Define globals objects + variables
    SettingsHandler { id: persistent_settings }
    ThemeHandler    { id: theme_handler       }
    WindowResizer   { id: window_resizer      }
    LoadingBar      { id: loading_bar         }
    WarningDialog   { id: warning_dialog      }

    property bool is_window_maximised: persistent_settings.open_window_as_maximised_on_startup
    readonly property string version_number: qsTr("v1.1")
    property string application_root_path : "This string gets updated right at start"
    property string all_ml_models: "This string gets updated right at start"

    // Add window attributes, and create app objects
    title: qsTr(">_next(log)")
    visibility: is_window_maximised ? (Window.Maximized | Window.Fullscreen) : Window.Windowed

    NextLog { id: next_log_app }
    MLLog   { id: ml_log_app   }

    Shortcut {
        sequence: "Z,I"
        onActivated: {
            if (app_loader.currentItem == next_log_app)
                next_log_app.information_page.resize_viewer(true)
            else
                ml_log_app.information_page.resize_viewer(true)
        }
    }

    Shortcut {
        sequence: "Z,O"
        onActivated: {
            if (app_loader.currentItem == next_log_app)
                next_log_app.information_page.resize_viewer(false)
            else
                ml_log_app.information_page.resize_viewer(false)
        }
    }
    
    StackView {
        id: app_loader
        anchors.fill: parent
        initialItem: next_log_app
        replaceEnter: Transition {}
        replaceExit: Transition {}
    }

    // Create connections/functions to handle signals sent from the backend
    Connections {
        target: backend

        // >_next(log) signals
        function onGenerated_log_file_signal(message) {
            loading_bar.close()
        }

        function onUpdated_log_model_signal(message) {
            loading_bar.close()
            if (message !== "Success") {
                warning_dialog.warning_text = qsTr(message)
                warning_dialog.open()
            }
        }

        // ML.log signals
        function onTraining_finished_signal(msg) {
            loading_bar.close()
            if (msg) {
                warning_dialog.warning_text = "Training failed: " + msg
                warning_dialog.open()
            }
        }

        function onTraining_statistics_signal(msg){
            msg = JSON.parse(msg)
            ml_log_app.train_statistics["model_name"] = msg["model_name"]
            ml_log_app.train_statistics["training_accuracy"] = msg["training_accuracy"]
            ml_log_app.train_statistics["testing_accuracy"] = msg["testing_accuracy"]
            ml_log_app.train_statistics["f1"] = msg["f1"]
            ml_log_app.train_statistics["precision"] = msg["precision"]
            ml_log_app.train_statistics["recall"] = msg["recall"]
            ml_log_app.training_parameters = msg["parameters"]
            backend.export_images()
            ml_log_app.reset_results()
        }

        function onInvalid_features_to_plot_signal(msg){
            loading_bar.close()
            if (msg) {
                warning_dialog.warning_text = "Invalid features: " + msg
                warning_dialog.open()
            }
        }

        function onPretrained_model_signal(msg){
            console.log(msg)
            msg = JSON.parse(msg)
            ml_log_app.pretrained_model = msg
        }

        function onPretrained_model_test_result_signal(msg, error){
            if (!error){
                msg = JSON.parse(msg)
                ml_log_app.pretrained_model["accuracy"] = msg["accuracy"]
                ml_log_app.pretrained_model["f1"] = msg["f1"]
                ml_log_app.pretrained_model["precision"] = msg["precision"]
                ml_log_app.pretrained_model["recall"] = msg["recall"]
            }
            else{
                warning_dialog.warning_text = error
                warning_dialog.open()
            }
        }

        function onPlot_open_signal(){
            loading_bar.open()
        }

        function onPlot_closed_signal(){
            loading_bar.close()
        }
    }
}
