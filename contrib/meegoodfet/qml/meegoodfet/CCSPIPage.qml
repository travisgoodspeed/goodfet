import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    function show(){
        if(GoodFET.isConnected()){
            appWindow.pageStack.push(ccspiPage);
        }
    }
    function update(){
        if(GoodFET.isConnected()){
            freq.text=(GoodFET.CCgetfreq()/1000000)+" MHz";
        }
    }
    onVisibleChanged: update();
    Timer {
        id: updateTimer
        interval: 1000; running: false; repeat: false
        onTriggered: {
            update();
        }
    }

    Label {
        id: title

        anchors.top: parent.top
        anchors.topMargin: 32

        text: "Chipcon SPI"
        platformStyle: LabelStyle {
            fontFamily: "Nokia Pure"
            fontPixelSize: 32
        }
    }

    Label {
        id: uid
        anchors.top: title.bottom
        anchors.topMargin: 16

        text: "Model: CC2420"
    }
    Label {
        id: freq
        anchors.top: uid.bottom
        anchors.topMargin: 16

        text: "Freq: unknown"
    }

    Button {
        id: setup
        anchors.top: parent.top
        anchors.topMargin: 224
        width: parent.width-16

        text: "Radio Setup"
        onClicked:{
            if(GoodFET.isConnected()){
                GoodFET.CCsetchan(channelSlider.value);
                GoodFET.CCsetup();
                updateTimer.start();
            }
        }
    }
    Label {
        id: channel
        text: "Channel: 11"
        anchors.top: setup.bottom
        anchors.topMargin: 16
    }
    Slider {
        id: channelSlider
        value: 11
        minimumValue: 11
        maximumValue: 26
        anchors.left: parent.left
        anchors.leftMargin: 125
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: setup.bottom
        anchors.topMargin: 16
        stepSize: 1
        onValueChanged:{
            if(GoodFET.isConnected()){
                channel.text="Channel: "+channelSlider.value
                GoodFET.CCsetchan(channelSlider.value);
                updateTimer.start();
            }
        }
    }

    Button {
        id: sniff
        anchors.top: channelSlider.bottom
        anchors.topMargin: 16
        width: parent.width-16

        text: "Packet Sniffer"
        onClicked:{
            //packet.text=GoodFET.CCrxpacketASCII();
            snifferPage.show();
        }
    }

    Button {
        id: transmit
        anchors.top: sniff.bottom
        anchors.topMargin: 16
        width: parent.width-16

        text: "Packet Transmit"
        onClicked:{
            //GoodFET.CCtxpacketASCII("09010882ffffffffc9d1");
            injectorPage.show();
        }
    }

}
