import QtQuick
import "../shared_controls"

Rectangle {
    id: left_menu_bar
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.left: parent.left
    width: theme_handler.left_bar_width
    color: theme_handler.primary_bar_colour

    function deactivate_all_pages() {
        home_button.is_active_page = false
        select_model_button.is_active_page = false
        results_button.is_active_page = false
        load_model_button.is_active_page = false
        info_button.is_active_page = false
        settings_button.is_active_page = false
    }

    function change_to_page(page_name) {
        deactivate_all_pages()
        switch (page_name) {
            case "Home":
                page_loader.replace(page_loader.currentItem, home_page)
                page_header.header_text = qsTr("Home");
                home_button.is_active_page = true
                break;
            case "Select model":
                page_loader.replace(page_loader.currentItem, select_model_page)
                page_header.header_text = qsTr("Model");
                select_model_button.is_active_page = true
                break;
            case "Results":
                page_loader.replace(page_loader.currentItem, results_page)
                page_header.header_text = qsTr("Results");
                results_button.is_active_page = true
                break;
            case "Load Model":
                page_loader.replace(page_loader.currentItem, load_model_page)
                page_header.header_text = qsTr("Load & Test Pretrained Model");
                load_model_button.is_active_page = true
                break;
            case "Info":
                page_loader.replace(page_loader.currentItem, information_page)
                page_header.header_text = qsTr("Information")
                info_button.is_active_page = true
                break
            case "Settings":
                page_loader.replace(page_loader.currentItem, settings_page)
                page_header.header_text = qsTr("Settings");
                settings_button.is_active_page = true
                break;
            default:
                console.log("Changed to unknown page!")
        }
    }

    Column {
        spacing: theme_handler.left_bar_buttons_vertical_spacing
        topPadding: theme_handler.top_padding

        LeftBarButton {
            id: home_button
            is_active_page: true
            icon_source: "../assets/home.png"
            onClicked: change_to_page("Home")
        }

        LeftBarButton {
            id: select_model_button
            is_active_page: false
            enabled: current_loaded_file_path !== ""
            icon_source: "../assets/select_model.png"
            onClicked: change_to_page("Select model")
        }

        LeftBarButton {
            id: results_button
            is_active_page: false
            enabled: current_loaded_file_path !== ""
            icon_source: "../assets/results.png"
            onClicked: {
                change_to_page("Results")
            }
        }

        LeftBarButton {
            id: load_model_button
            is_active_page: false
            enabled: current_loaded_file_path !== ""
            icon_source: "../assets/upload.png"
            onClicked: change_to_page("Load Model")
        }
    }

    LeftBarButton {
        id: info_button
        is_active_page: false
        icon_source: "../assets/info.png"
        anchors.bottom: settings_button.top
        anchors.bottomMargin: theme_handler.left_bar_buttons_vertical_spacing
        onClicked: change_to_page("Info")
    }

    LeftBarButton {
        id: settings_button
        is_active_page: false
        icon_source: "../assets/settings.png"
        anchors.bottom: switch_button.top
        anchors.bottomMargin: theme_handler.left_bar_buttons_vertical_spacing
        onClicked: change_to_page("Settings")
    }

    LeftBarButton {
        id: switch_button
        is_active_page: false
        icon_source: "../assets/switch_ml_on.png"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: theme_handler.left_bar_buttons_vertical_spacing
        onClicked: {
            main_window.title = qsTr(">_next(log)")
            next_log_app.top_bar.app_title = qsTr("Synthetic Event Log Generation Tool")
            app_loader.replace(app_loader.currentItem, next_log_app)
        }
    }
}
