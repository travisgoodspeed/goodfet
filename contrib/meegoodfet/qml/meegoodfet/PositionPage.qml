import QtQuick 1.1
import QtMobility.location 1.1
import com.nokia.meego 1.0

Page {
    function show(){
        appWindow.pageStack.push(positionPage);
    }
    function setActive(active){
        positionSource.active=active;
    }

    id: top
    anchors.fill: parent

    PositionSource {
        id: positionSource
        updateInterval: 1000
        active: false
        // nmeaSource: "nmealog.txt"
        onPositionChanged: {
            GoodFET.writelog("position: "+
                             positionSource.position.coordinate.longitude+","+
                             positionSource.position.coordinate.latitude);
            GoodFET.writelog("timestamp: "+positionSource.position.timestamp);
        }
    }
    Column {
        Text {text: "<==== PositionSource ====>"}
        Text {text: "positioningMethod: "  + printableMethod(positionSource.positioningMethod)}
        Text {text: "nmeaSource: "         + positionSource.nmeaSource}
        Text {text: "updateInterval: "     + positionSource.updateInterval}
        Text {text: "active: "     + positionSource.active}
        Text {text: "<==== Position ====>"}
        Text {text: "latitude: "   + positionSource.position.coordinate.latitude}
        Text {text: "longitude: "   + positionSource.position.coordinate.longitude}
        Text {text: "altitude: "   + positionSource.position.coordinate.altitude}
        Text {text: "speed: " + positionSource.position.speed}
        Text {text: "timestamp: "  + positionSource.position.timestamp}
        Text {text: "altitudeValid: "  + positionSource.position.altitudeValid}
        Text {text: "longitudeValid: "  + positionSource.position.longitudeValid}
        Text {text: "latitudeValid: "  + positionSource.position.latitudeValid}
        Text {text: "speedValid: "     + positionSource.position.speedValid}
    }
    function printableMethod(method) {
        if (method == PositionSource.SatellitePositioningMethod)
            return "Satellite";
        else if (method == PositionSource.NoPositioningMethod)
            return "Not available"
        else if (method == PositionSource.NonSatellitePositioningMethod)
            return "Non-satellite"
        else if (method == PositionSource.AllPositioningMethods)
            return "All/multiple"
        return "source error";
    }
}
