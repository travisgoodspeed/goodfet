import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    function show(){
        if(GoodFET.isConnected()){
            appWindow.pageStack.push(monitorPage);
        }
    }

    Label {
        id: title

        anchors.top: parent.top
        anchors.topMargin: 32
        anchors.verticalCenter: parent.verticalCenter

        text: "Monitor"
        platformStyle: LabelStyle {
            fontFamily: "Nokia Pure"
            fontPixelSize: 32
        }
    }

}
