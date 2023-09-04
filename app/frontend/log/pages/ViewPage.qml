import QtQuick
import QtWebEngine

Item {
    clip: true

    function reloadWebEngineView() {
        web_engine_view.reload()
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        WebEngineView {
            id: web_engine_view
            anchors.fill: parent
            url: Qt.resolvedUrl("../html/view_bpm.html")
            onLoadingChanged: {
                if (loadProgress === 100)
                    buffer_rectangle_opacity_animation.start()
            }
        }

        // Below is a hacky but very aesthitic way of fixing the "flashing" when the WebEngineView is loading lol.
        // Delete line 13 and the below ones to see what happens without it.
        Rectangle {
            id: buffer_rectangle
            anchors.fill: web_engine_view
            color: theme_handler.background_colour
        }

        NumberAnimation {
            id: buffer_rectangle_opacity_animation
            target: buffer_rectangle
            property: "opacity"
            from: 1
            to: 0
            duration: 1000
            easing.type: Easing.InOutSine
        }
    }
}
