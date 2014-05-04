import QtQuick 1.1
import com.nokia.meego 1.0


Page {
    //This shouldn't be hardcoded.
    property string btAddress: "00:06:66:42:A9:4A"  //GoodFET

    property bool connecting: false
    property Page scanner

    function show(){
        appWindow.pageStack.clear();
        appWindow.pageStack.push(mainPage);
        //appWindow.pageStack.replace(mainPage);
    }

    Label {
        id: title

        anchors.top: parent.top
        anchors.topMargin: 32
        anchors.verticalCenter: parent.verticalCenter

        text: "GoodFET for Meego"
        platformStyle: LabelStyle {
            fontFamily: "Nokia Pure"
            fontPixelSize: 32
        }
    }

    Button {
        id: macAddress
        anchors.top: parent.top
        anchors.topMargin: 64

        text: btAddress
        onClicked:{
            scannerPage.startScan();
        }
    }

    Switch {
        id: blueSwitch
        anchors.top: parent.top
        anchors.topMargin: 64
        anchors.left: parent.right
        anchors.leftMargin: -96

        anchors.verticalCenter: parent.verticalCenter

        checked: false
        onCheckedChanged: {
            console.log("switch: " + checked)
            if (blueSwitch.checked == false) {
                console.log("Disconnecting by switch.");
                builddate.text="Disconnected";
                GoodFET.close();
            } else {
                console.log("Connecting to "+btAddress);
                builddate.text="Connecting";
                GoodFET.open(btAddress);
                connecting=true;
            }
        }
    }

    Label {
        id: builddate
        anchors.top: macAddress.bottom
        anchors.topMargin: 16

        text: "Disconnected"
    }
    Label {
        id: gps
        anchors.top: builddate.bottom
        anchors.topMargin: 16

        text: "GPS Logging"
    }

    Switch {
        id: gpsSwitch
        anchors.top: gps.top
        anchors.left: parent.right
        anchors.leftMargin: -96

        checked: false
        onCheckedChanged: {
            positionPage.setActive(gpsSwitch.checked);
        }
    }

    Button {
        id: monitor
        anchors.top: parent.top
        anchors.topMargin: 300
        width: parent.width-16

        text: "Monitor"
        onClicked:{
            monitorPage.show();
        }
    }

    Button {
        id: ccspi
        anchors.top: monitor.bottom
        anchors.topMargin: 16
        width: parent.width-16

        text: "Chipcon SPI"
        onClicked:{
            ccspiPage.show();
        }
    }

    Button {
        id: nrf
        anchors.top: ccspi.bottom
        anchors.topMargin: 16
        width: parent.width-16

        text: "Nordic RF"
        onClicked:{
            //nrfPage.show();
        }
    }


    Image {
        anchors.top: nrf.bottom
        anchors.topMargin: 16

        width: parent.width
        //height: 100
        fillMode: Image.PreserveAspectFit
        smooth: true
        source: "goodfet.png"
    }




    //TODO replace this with proper events.
    Timer {
        interval: 1000; running: true; repeat: true
        onTriggered: {
            if (GoodFET.isConnected()) {
                connecting=false;
                builddate.text="Firmware: "+GoodFET.getFirmwareVersion();
                //freq.text=GoodFET.CCgetfreq()+" Hz";
            }else{
                if(blueSwitch.checked && connecting==false)
                    blueSwitch.checked=false;
            }
        }
    }

}
