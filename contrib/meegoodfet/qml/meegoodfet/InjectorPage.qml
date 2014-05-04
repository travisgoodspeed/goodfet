import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    function show(){
        if(GoodFET.isConnected()){
            appWindow.pageStack.push(injectorPage);
        }
    }
    function insertPacket(packet){
        packetModel.insert(0,{name: packet});
        //packetModel.append({name: packet});
        titlelabel.text=packetModel.count+" packets.";
    }

    id: top
    anchors.fill: parent


    ListModel {
        id: packetModel
        /*
        ListElement {
            name: "0f010882ffffffffdeadbeefbabe"
        }
        */
        ListElement {
            name: "19010882cafebabe00000000a709010882ffffffffc9d1"
        }
    }

    Label {
        id: titlelabel
        anchors.top:  top.top
        anchors.margins: 3
        width: parent.width-6
        text: "Injecting..."
    }
    Switch {
        id: injectSwitch
        anchors.top: parent.top
        anchors.margins: 3
        anchors.right: parent.right

        //anchors.verticalCenter: parent.verticalCenter

        checked: false

        onCheckedChanged: {
            console.log("injectSwitch: " + checked);
            injectTimer.running=injectSwitch.checked;
        }
    }
    /*
    Button {
        id: clearButton
        anchors.top: parent.top
        anchors.margins: 3
        anchors.right: injectSwitch.left
        text: "Clear"
        width: 90
        onClicked: packetModel.clear();
    }
    */

    Rectangle {
        width: parent.width
        height: parent.height-top
        anchors.top: injectSwitch.bottom
        anchors.margins: 20

        Component {
                 id: packetDelegate
                 Rectangle {
                     id: wrapper
                     width: parent.width
                     height: packetInfo.height
                     //color: ListView.isCurrentItem ? "black" : "red"
                     Text {
                         id: packetInfo
                         text: name
                         font.family: "courier"
                         //color: wrapper.ListView.isCurrentItem ? "red" : "black"
                     }
                 }
             }

        ListView {
            anchors.fill: parent
            model: packetModel
            delegate: packetDelegate

            highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            focus: true
        }
    }



    //TODO replace this with proper events.
    Timer {
        id: injectTimer
        interval: 100; running: false; repeat: true
        onTriggered: {
            if (GoodFET.isConnected()) {
                if(injectSwitch.checked){
                    //GoodFET.CCtxpacketASCII("19010882cafebabe00000000a709010882ffffffffc9d1");
                    if(GoodFET.getQueueLength()==0)
                        GoodFET.CCtxpacketASCII("19010882cafebabe00000000a709010882ffffffffc9d1");
                }
            }else{
                injectSwitch.checked=false;
            }
        }
    }

}
