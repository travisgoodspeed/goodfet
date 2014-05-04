import QtQuick 1.1
import com.nokia.meego 1.0
import QtMobility.connectivity 1.2

Page {
    id: top

    property BluetoothService currentService
    property alias minimalDiscovery: discoveryModel.minimalDiscovery
    property alias uuidFilder: discoveryModel.uuidFilter
    property bool scanRequested: false

    anchors.fill: parent

    function startScan(){
        scanRequested=true;
        appWindow.pageStack.push(scannerPage);
        discoveryModel.discovery=true;
    }

    BluetoothHostModel {
        id: btModel
    }

    BluetoothDiscoveryModel {
        id: discoveryModel
        minimalDiscovery: true
        discovery: false
        onDiscoveryChanged: {
            //busy.running = discovery;
            if(!discovery && scanRequested)
                singleSelectionDialog.open();
        }
        onNewServiceDiscovered:{
            console.log("Found new service " + service.deviceAddress + " " + service.deviceName + " " + service.serviceName);
            btModel.append({
                               "name":          service.deviceName+" "+service.serviceName,
                               "deviceName":    service.deviceName,
                               "deviceAddress": service.deviceAddress,
                               "serviceName":   service.serviceName
                           });
        }

        //uuidFilter: "00001101-0000-1000-8000-00805F9B34FB"
    }

    // Create a selection dialog with a title and list elements to choose from.
    SelectionDialog {
        id: singleSelectionDialog
        titleText: "Bluetooth Scan"
        selectedIndex: 1
        model: btModel
        onAccepted: {
            mainPage.btAddress=singleSelectionDialog.model.get(singleSelectionDialog.selectedIndex).deviceAddress;
            saveAddress();
            pageStack.pop(scannerPage);
        }

        onRejected: pageStack.pop(scannerPage);
    }

    Label {
        id: titlelabel
        anchors.top:  top.top
        anchors.margins: 3
        width: parent.width-6
        text: "Scanning..."
    }

    Button {
        id: cancelbutton
        anchors.bottom:  parent.bottom
        anchors.margins: 3
        width: parent.width-6
        text: "Cancel Scan"
        onClicked:{
            scanRequested=false;
            discoveryModel.setDiscovery(false);
            pageStack.pop(scannerPage);
        }
    }
}
