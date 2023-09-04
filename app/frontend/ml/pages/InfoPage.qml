import QtQuick
import QtQuick.Pdf
import QtQuick.Layouts

Item {
    clip: true

    function resize_viewer(shouldZoomIn) {
        if (page_loader.currentItem === this) {
            if (shouldZoomIn)
                viewer.renderScale *= Math.sqrt(2)
            else
                viewer.renderScale /= Math.sqrt(2)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: theme_handler.background_colour

        PdfMultiPageView {
            id: viewer
            clip: true
            anchors.fill: parent
            document: info_document
        }
    }
}
