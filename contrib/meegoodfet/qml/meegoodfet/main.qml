import QtQuick 1.1
import com.nokia.meego 1.0
import "database.js" as Storage

PageStackWindow {
    id: appWindow

    initialPage: mainPage


    ScannerPage {
        id: scannerPage
        orientationLock: PageOrientation.LockPortrait
        //tools: commonTools
    }
    MonitorPage {
        id: monitorPage
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }
    CCSPIPage {
        id: ccspiPage
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }
    SnifferPage {
        id: snifferPage
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }
    InjectorPage {
        id: injectorPage
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }
    PositionPage {
        id: positionPage
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }

    MainPage {
        id: mainPage
        btAddress: "00:06:66:42:A9:4A"
        orientationLock: PageOrientation.LockPortrait
        tools: commonTools
    }

    Component.onCompleted: {
        // Initialize the database
        Storage.initialize();
        mainPage.btAddress = Storage.getSetting("btAddress");
    }

    function saveAddress(){
        Storage.setSetting("btAddress", mainPage.btAddress);
    }



    ToolBarLayout {
        id: commonTools
        visible: true
        ToolIcon {
            platformIconId: "toolbar-view-menu"
            anchors.right: (parent === undefined) ? undefined : parent.right
            onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
        ToolIcon {
            platformIconId: "toolbar-back"
            anchors.left: (parent === undefined) ? undefined : parent.left
            onClicked: pageStack.pop();
        }
    }

    Menu {
        id: myMenu
        visualParent: pageStack
        MenuLayout {
            /*
            MenuItem {
                text: qsTr("Bluetooth Discovery")
                onClicked: scannerPage.startScan();
            }*/
            MenuItem {
                text: qsTr("Position")
                onClicked: positionPage.show();
            }
            MenuItem {
                text: qsTr("Monitor")
                onClicked: monitorPage.show();
            }
            MenuItem {
                text: qsTr("Chipcon SPI")
                onClicked: ccspiPage.show();
            }
            MenuItem {
                text: qsTr("Chipcon Sniffer")
                onClicked: snifferPage.show();
            }
            MenuItem {
                text: qsTr("Chipcon Injector")
                onClicked: injectorPage.show();
            }
            MenuItem {
                text: qsTr("Main")
                onClicked: mainPage.show();
            }
        }
    }
}
