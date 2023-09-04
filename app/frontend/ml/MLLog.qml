import QtQuick
import QtQuick.Controls
import QtQuick.Pdf
import "pages"
import "../shared_controls"



Item {
    id: ml_log
    property string current_loaded_file_path: ""
    property var train_statistics: {
        "training_accuracy" : "",
        "testing_accuracy" : "",
        "f1" : "",
        "precision" : "",
        "recall" : ""
    }
    property var training_parameters: null
    property var pretrained_model: {
        "model": "please select a model",
        "date": "",
        "train_size": "",
        "accuracy": "",
        "f1" : "",
        "precision" : "",
        "recall" : ""
    }
    property string pretrained_model_test_result: ""
    property alias information_page: information_page
    property alias top_bar: top_bar

    function reset_results(){
        results_page.reset_results()
    }

    Rectangle {
        id: app_container
        anchors.fill: parent

        // Top/Sidebar and PageHeader/Footer Creations
        TopBar      { id: top_bar }
        MLLeftBar   { id: left_bar }
        PageHeader  { id: page_header }
        FooterBar   { id: footer_bar }

        Rectangle {
            id: invisible_right_bar
            color: theme_handler.background_colour
            anchors {
                top: page_header.bottom
                bottom: footer_bar.top
                right: app_container.right
            }
            width: theme_handler.page_loader_margins
        }

        Rectangle {
            id: invisible_left_bar
            color: theme_handler.background_colour
            anchors {
                top: page_header.bottom
                bottom: footer_bar.top
                left: left_bar.right
            }
            width: theme_handler.page_loader_margins
        }

        Rectangle {
            id: loader_background
            anchors {
                top: page_header.bottom
                left: invisible_left_bar.right
                right: invisible_right_bar.left
                bottom: footer_bar.top
            }
            color: theme_handler.background_colour

            PdfDocument {
                id: info_document
                source: persistent_settings.use_light_theme_on_startup ? "../assets/info_ml_light.pdf" : "../assets/info_ml_dark.pdf"
            }

            // Page Creations
            Home          { id: home_page         }
            SelectModel   { id: select_model_page }
            LoadModel     { id: load_model_page   }
            Results       { id: results_page      }
            InfoPage      { id: information_page  }
            SettingsPage  { id: settings_page     }

            // Create Dynamic Loader -- will display each "page"
            StackView {
                id: page_loader
                anchors.fill: loader_background
                initialItem: home_page
                replaceEnter: Transition {}
                replaceExit: Transition {}
            }
        }
    }
}
