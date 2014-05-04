import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    function show(){
        if(GoodFET.isConnected()){
            appWindow.pageStack.push(snifferPage);
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
            name: "Something"
            deviceName: "RN42-A94A"
            deviceAddress: "00:06:66:42:A9:4A"
        }*/
    }

    Label {
        id: titlelabel
        anchors.top:  top.top
        anchors.margins: 3
        width: parent.width-6
        text: "0 packets."
    }
    Switch {
        id: sniffSwitch
        anchors.top: parent.top
        anchors.margins: 3
        anchors.right: parent.right

        checked: false

        onCheckedChanged: {
            console.log("sniffSwitch: " + checked);
            sniffTimer.running=sniffSwitch.checked;
        }
    }
    Button {
        id: clearButton
        anchors.top: parent.top
        anchors.margins: 3
        anchors.right: sniffSwitch.left
        text: "Clear"
        width: 90
        onClicked: packetModel.clear();
    }

    Rectangle {
        width: parent.width
        height: parent.height-top
        anchors.top: clearButton.bottom
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
        id: sniffTimer
        interval: 1000; running: false; repeat: true
        onTriggered: {
            if (GoodFET.isConnected()) {
                if(sniffSwitch.checked){
                    var packet=GoodFET.CCrxpacketASCII();
                    if(packet.length>0)
                        snifferPage.insertPacket(packet);
                }
            }else{
                sniffSwitch.checked=false;
            }
        }
    }

}
