import QtQuick
import QtQuick.Controls.Basic

Dialog {
    property alias warning_text: label.text
    readonly property int dialog_padding: 15

    modal: true
    anchors.centerIn: Overlay.overlay
    closePolicy: Popup.NoAutoClose
    padding: dialog_padding
    height: 3 * theme_handler.normal_button_width
    width: main_window.width / 1.5
    z: 10

    background: Rectangle {
        radius: theme_handler.rectangle_radius
        color: theme_handler.background_colour
        border {
            color: theme_handler.primary_bar_colour
            width: theme_handler.border_width + 2
        }
        anchors.fill: parent
    }

    header: Text {
        text: qsTr("Warning/Error:")
        height: theme_handler.normal_button_width
        color: theme_handler.primary_text_colour
        font {
            bold: true
            family: theme_handler.font_family
            pointSize: theme_handler.rules_font_size
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    contentItem: Label {
        id: label
        color: theme_handler.primary_text_colour
        text: qsTr("")
        font {
            family: theme_handler.font_family
            pointSize: theme_handler.font_text_size
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.Wrap
    }

    footer: DialogButtonBox {
        alignment: Qt.AlignHCenter
        implicitHeight: theme_handler.normal_button_width
        background: Rectangle {
            anchors.fill: parent
            anchors.margins: theme_handler.border_width + 2
            color: theme_handler.background_colour
        }
        NormalButton {
            text: qsTr("R.I.P")
            anchors.fill: parent
            DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
        }
    }
}
