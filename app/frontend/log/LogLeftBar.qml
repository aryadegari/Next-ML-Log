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
        view_bpmn_button.is_active_page = false
        rule_maker_button.is_active_page = false
        generate_logs_button.is_active_page = false
        info_button.is_active_page = false
        settings_button.is_active_page = false
    }

    function change_to_page(page_name) {
        deactivate_all_pages()
        switch (page_name) {
        case "Home":
            page_loader.replace(page_loader.currentItem, home_page)
            page_header.header_text = qsTr("Home")
            home_button.is_active_page = true
            break
        case "View BPM":
            page_loader.replace(page_loader.currentItem, view_page)
            page_header.header_text = qsTr("View Business Process Model")
            view_bpmn_button.is_active_page = true
            break
        case "Rules Maker":
            page_loader.replace(page_loader.currentItem, rules_page)
            page_header.header_text = qsTr("Rules")
            rule_maker_button.is_active_page = true
            break
        case "Generate (Adapted) Logs":
            page_loader.replace(page_loader.currentItem, generate_page)
            page_header.header_text = qsTr("Generate (Adapted) Logs")
            generate_logs_button.is_active_page = true
            break
        case "Info":
            page_loader.replace(page_loader.currentItem, information_page)
            page_header.header_text = qsTr("Information")
            info_button.is_active_page = true
            break
        case "Settings":
            page_loader.replace(page_loader.currentItem, settings_page)
            page_header.header_text = qsTr("Settings")
            settings_button.is_active_page = true
            break
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
            id: view_bpmn_button
            is_active_page: false
            enabled: currently_loaded_bpmn_file !== ""
            icon_source: "../assets/view_bpmn.png"
            onClicked: change_to_page("View BPM")
        }

        LeftBarButton {
            id: rule_maker_button
            is_active_page: false
            enabled: (currently_loaded_bpmn_file !== "") && (currently_loaded_mxml_file !== "")
            icon_source: "../assets/edit.png"
            onClicked: change_to_page("Rules Maker")
        }

        LeftBarButton {
            id: generate_logs_button
            is_active_page: false
            enabled: (currently_loaded_bpmn_file !== "") && (currently_loaded_mxml_file !== "") && parse_successful
            icon_source: "../assets/save.png"
            onClicked: change_to_page("Generate (Adapted) Logs")
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
        icon_source: "../assets/switch_next_on.png"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: theme_handler.left_bar_buttons_vertical_spacing
        onClicked: {
            main_window.title = qsTr("ML.log")
            ml_log_app.top_bar.app_title = qsTr("Machine Learning on Business Process Data")
            app_loader.replace(app_loader.currentItem, ml_log_app)
        }
    }
}
