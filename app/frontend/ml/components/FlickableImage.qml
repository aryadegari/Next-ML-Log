import QtQuick
import QtQuick.Window 
import QtQuick.Dialogs 


Item{
    property string image_source: "../../assets/active_image.png"

    Rectangle{
        id: view_model_fancy
        anchors.fill: parent
        radius: theme_handler.rectangle_radius
        color: theme_handler.background_colour

        Item {
            id: image_area_fancy
            anchors.fill: parent

            Flickable {
                anchors.fill: parent
                contentWidth: Math.max(image.width * image.scale, image_area_fancy.width)
                contentHeight: Math.max(image.height * image.scale, image_area_fancy.height)
                clip: true

                Image {
                    id: image

                    property real zoom: 0.0
                    property real zoomStep: 0.1

                    asynchronous: true
                    cache: false
                    smooth: true
                    antialiasing: true
                    mipmap: true

                    anchors.centerIn: parent
                    fillMode: Image.PreserveAspectFit
                    transformOrigin: Item.Center
                    scale: Math.min(image_area_fancy.width / width, image_area_fancy.height / height, 1) + zoom

                    source: image_source
                }
            }

            // Mouse zoom
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                onWheel: (wheel) => {
                    if (wheel.angleDelta.y > 0)
                        image.zoom = Number((image.zoom + image.zoomStep).toFixed(1))
                    else if (image.zoom > 0)
                        image.zoom = Number((image.zoom - image.zoomStep).toFixed(1))

                    wheel.accepted = true
                }
            }
        }
    }
}