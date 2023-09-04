import QtQuick

Item {
    // Menu Layout Constants;
    readonly property int top_bar_height: 35
    readonly property int footer_bar_height: top_bar_height
    readonly property int left_bar_width: 1.5 * top_bar_height
    readonly property int left_bar_button_width: left_bar_width
    readonly property int left_bar_button_height: left_bar_width
    readonly property int left_bar_button_edge_width: 5
    readonly property int left_bar_buttons_vertical_spacing: 25
    readonly property int normal_button_width: 100
    readonly property int rectangle_radius: 5
    readonly property int border_width: 2
    readonly property int top_padding: top_bar_height + left_bar_buttons_vertical_spacing
    readonly property int upload_area_height: 50
    readonly property int text_margins: 20

    // Page Layout Constants;
    readonly property int page_top_margins: 25
    readonly property int header_height: 2 * top_bar_height
    readonly property int page_loader_margins: 50
    readonly property int page_item_spacing: 25

    // Fonts
    readonly property string font_family: "Source Code Pro"
    readonly property int font_page_title_size: 24
    readonly property int font_text_size: 16
    readonly property int font_topbar_and_footerbar_size: 12
    readonly property int rules_font_size: 20

    // Theme Colouring;
    property string primary_bar_colour
    property string secondary_bar_colour
    property string primary_text_colour
    property string secondary_text_colour
    property string background_colour
    property string left_bar_button_clicked_colour
    property string left_bar_button_hovered_colour
    property string left_bar_button_edge_colour
    property string left_bar_button_bg_colour
    property string alt_icon_colour
    property string hover_button_text_colour
    property string disabled_red_colour
    property string enabled_green_colour
    property string rules_background_colour

    property bool is_currently_light_theme

    function invert_theme() {
        if (is_currently_light_theme) theme_handler.set_to_dark_theme()
        else theme_handler.set_to_light_theme()
    }


    function set_to_light_theme() {
        primary_bar_colour = "#B4B6B6"
        secondary_bar_colour = "#D6D7D7"
        primary_text_colour = "#3D476B"
        secondary_text_colour = "#5D6DA2"
        background_colour = "#E8E8E8"
        left_bar_button_bg_colour = primary_bar_colour
        left_bar_button_hovered_colour = secondary_bar_colour
        left_bar_button_clicked_colour = secondary_bar_colour
        left_bar_button_edge_colour = secondary_text_colour
        hover_button_text_colour = "#6474A6"
        alt_icon_colour = hover_button_text_colour
        rules_background_colour = "#F7F7F7"
        disabled_red_colour = "#F29D9C"
        enabled_green_colour = "#7ECB48"
        is_currently_light_theme = true
        persistent_settings.use_light_theme_on_startup = true
        backend.changed_theme(true) // "true" to express changed to light_theme
    }

    function set_to_dark_theme() {
        primary_bar_colour = "#1B1D1F"
        secondary_bar_colour = "#2A2C35"
        primary_text_colour = "#F7F7F7"
        secondary_text_colour = "#BABCC4"
        background_colour = "#363945"
        left_bar_button_bg_colour = primary_bar_colour
        left_bar_button_hovered_colour = secondary_bar_colour
        left_bar_button_clicked_colour = secondary_bar_colour
        left_bar_button_edge_colour = secondary_text_colour
        hover_button_text_colour = "#A4A7B2"
        alt_icon_colour = hover_button_text_colour
        rules_background_colour = "#4F5364"
        disabled_red_colour = "#912121"
        enabled_green_colour = "#0F7011"
        is_currently_light_theme = false
        persistent_settings.use_light_theme_on_startup = false
        backend.changed_theme(false) // "false" to express changed to dark_theme
    }

    Component.onCompleted: {
        is_currently_light_theme = persistent_settings.use_light_theme_on_startup
        if (is_currently_light_theme) set_to_light_theme()
        else set_to_dark_theme()
    }
}
