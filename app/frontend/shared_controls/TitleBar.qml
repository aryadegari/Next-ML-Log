import QtQuick

Rectangle {
    id: area
    anchors.fill: parent
    color: theme_handler.primary_bar_colour

    // Frontend Logic;
    function minimise() {
        is_window_maximised = false
        maximise_restore_button.icon_source = "../assets/maximise.png"
        main_window.showMinimized()
    }

    function maximize_restore() {
        if (is_window_maximised) {
            main_window.showNormal()
            is_window_maximised = false
        } else {
            main_window.showMaximized()
            is_window_maximised = true
        }
    }

    Row {
        height: theme_handler.top_bar_height
        width: theme_handler.top_bar_height * 3
        anchors.right: area.right
        anchors.rightMargin: 0

        TitleBarButton {
            id: minimise_button
            icon_source: "../assets/minimise.png"
            onClicked: minimise()
        }

        TitleBarButton {
            id: maximise_restore_button
            icon_source: is_window_maximised ? "../assets/restore.png" : "../assets/maximise.png"
            onClicked: maximize_restore()
        }

        TitleBarButton {
            id: quit_button
            icon_source: "../assets/quit.png"
            onClicked: main_window.close()
        }
    }
}
