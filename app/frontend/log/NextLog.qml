import QtQuick
import QtQuick.Controls
import QtQuick.Pdf
import "pages"
import "../shared_controls"

Item {
    // Define globals
    property alias information_page: information_page
    property string currently_loaded_bpmn_file: qsTr("")
    property string currently_loaded_mxml_file: qsTr("")
    property string current_output_file_destination: qsTr("")
    property bool parse_successful: false
    property bool has_tried_to_parse: false
    property bool save_original_file: persistent_settings.check_save_original
    property alias page_loader: page_loader
    property alias top_bar: top_bar

    Rectangle {
        id: app_container
        anchors.fill: parent

        // Top/Sidebar and PageHeader/Footer Creations
        TopBar { id: top_bar }
        LogLeftBar { id: left_bar }
        PageHeader { id: page_header }
        FooterBar { id: footer_bar }

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

            // Initialise info_document (a PdfDocument object) for Info.qml
            PdfDocument {
                id: info_document
                source: persistent_settings.use_light_theme_on_startup ? "../assets/info_log_light.pdf" : "../assets/info_log_dark.pdf"
            }

            // Page Creations
            HomePage        { id: home_page }
            ViewPage        { id: view_page }
            RulesPage       { id: rules_page }
            GeneratePage    { id: generate_page }
            InfoPage        { id: information_page }
            SettingsPage    { id: settings_page }

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
