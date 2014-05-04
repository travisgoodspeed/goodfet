#ifndef GOODFET_H
#define GOODFET_H

#include <QObject>
#include <QQueue>
#include <QFile>
#include <QTextStream>
#include <QDate>

#include <iostream>
#include <fstream>

//Bluetooth stuff.
//Remember to include QtConnectivity in the .pro file!
#include <QtConnectivity/QBluetoothAddress>
#include <QtConnectivity/QBluetoothSocket>
#include <QtConnectivity/QBluetoothUuid>

#include <QtCore/QDataStream>
#include <QtCore/QByteArray>
#include <QtCore/QStringList>

using QTM_PREPEND_NAMESPACE(QBluetoothSocket);
using QTM_PREPEND_NAMESPACE(QBluetoothAddress);
using QTM_PREPEND_NAMESPACE(QBluetoothUuid);

//! GoodFET Client class.  EXPERIMENTAL
class GoodFET: public QObject
{
    Q_OBJECT
public:

    explicit GoodFET(QObject *parent = 0);
    QBluetoothSocket *socket;
    QBluetoothAddress *adr;
    QBluetoothUuid *uuid;
    QString version;

    //! Transmit a packet.
    Q_INVOKABLE void CCtxpacket(char *packet,qint64 len){
        //Strobe to TX mode.
        CCstrobe(0x04); //0x05 for CCA.
        //self.writecmd(self.CCSPIAPP,0x81,len(packet),packet);
        cmd(0x51,0x81,len,packet);
    }
    //! Transmit a packet from its ASCII HEX interpretation. Useful with QML.
    Q_INVOKABLE void CCtxpacketASCII(QString packet){
        QByteArray packetbytes=QByteArray::fromHex(packet.toAscii());
        CCtxpacket(packetbytes.data(),packetbytes.length());
        qDebug("Transmitting packet of %i bytes",
               packetbytes.length());
    }

    //! Inbound 802.15.4 packet queue.
    QQueue<QByteArray> CCinpackets;
    Q_INVOKABLE int getQueueLength(){
        return outbuffer.length();
    }

    //! Receive a packet, iff one is waiting.
    Q_INVOKABLE QByteArray CCrxpacket(bool returnpacket=true){
        char data[]={0x00};

        //If one is already waiting, return it.
        if(!CCinpackets.isEmpty() && returnpacket){
            qDebug("Returning a dequeued packet.");
            return CCinpackets.dequeue();
        }

        //Request a packet only if we aren't already doing it.
        cmd(0x51,0x80,1,data);

        if(CCcountdown)
            CCcountdown--;
        return QByteArray();

    }
    //! Receive a packet as ASCII-formatted hexadecimal.
    Q_INVOKABLE QString CCrxpacketASCII(){
        QByteArray b=CCrxpacket(true);
        return b.toHex();
    }

    //! Setup the Chipcon radio for use.
    Q_INVOKABLE void CCsetup(){
        cmd(0x51,0x10,0x00,0); //CCSPI/SETUP
        CCstrobe(0x01); //SXOSCON
        CCstrobe(0x02); //SCAL
        CCpoke(0x11,0x0AC2&(~0x0800)); //MDMCTRL0, cleared to be promiscuous
        //CCpoke(0x12,0x0500&(~0x200)); //MDMCTRL1, 0x200 cleared to ignore CRC.
        CCpoke(0x12,0x0500); //MDMCTRL1, 0x200 set to check CRC.
        CCpoke(0x1C,0x007F); //IOCFG0
        CCpoke(0x19,0x01C4); //SECCTRL0, disabling crypto
        CCpeek(0x18); //Grab frequency.
        //Strobe to RX mode.
        CCstrobe(0x03); //RXON
    }
    //! Set the frequency.
    Q_INVOKABLE void CCsetfreq(qint64 freq){
        qDebug()<<"Setting freq="<<freq;
        qint64 mhz=freq/1000000;
        qint16 fsctrl=CCregs[0x18]&(~0x3FF);
        fsctrl=fsctrl|(mhz-2048);
        CCpoke(0x18,fsctrl);
        CCstrobe(0x02);  //SCAL
        CCpeek(0x18);    //Reload the cached value.
        //Strobe to RX mode.
        CCstrobe(0x03); //SRXON
        return;
    }
    //! Get the frequency.
    Q_INVOKABLE qint64 CCgetfreq(){
        qint64 fsctrl=CCpeek(0x18);
        qint64 freq=2048+(fsctrl&0x3FF);
        return freq*1000000;
    }

    //! Set the Chipcon radio's channel.
    Q_INVOKABLE void CCsetchan(qint8 chan){
        qint64 c=chan;
        if(chan<11 or chan>26){
            qDebug("WARNING: Channel %i is outside the range of 11 to 26. Trying anyways.",chan);

        }
        log << "Channel: " << c << std::endl;
        CCsetfreq( ( (c-11)*5 + 2405 ) * 1000000 );
    }
    //! Get the Chipcon radio's channel.
    Q_INVOKABLE qint8 CCgetchan(){
        return 0;
    }

    //! Send and receive SPI data through the Chipcon chip. There is no return
    Q_INVOKABLE void CCtrans(char *data, qint16 len){
        synccmd(0x51,0x00,len,data);
        return;
    }
    //! Write a 16 bit value into an 8 bit register.
    Q_INVOKABLE void CCpoke(qint8 reg, qint16 val){
        char data[3];
        //Address is just one byte.
        data[0]=reg;
        //Data in Big Endian.
        data[1]=(val>>8);
        data[2]=val&0xFF;
        synccmd(0x51,0x03,3,data);
    }
    //! Strobe a Chipcon register.
    Q_INVOKABLE void CCstrobe(qint8 reg){
        char data[1];
        data[0]=reg;
        synccmd(0x51,0x00,1,data);
    }
    //! Returns last received CC reg value, and optionally requests a new one.
    Q_INVOKABLE qint16 CCpeek(qint8 reg, bool refresh=true){
        char data[3];
        data[0]=reg;
        data[1]=0;
        data[2]=0;
        qDebug("Peeking r%02x is really slow over Bluetooth. Faking the reply.",reg);
        if(refresh)
            cmd(0x51,0x02,3,data);
        return(CCregs[reg]);
    }


    //! Open a socket to the specified address.
    Q_INVOKABLE QString open(const QString &address){


        // Connect to service
        socket = new QBluetoothSocket(QBluetoothSocket::RfcommSocket);
        adr=new QBluetoothAddress(address);
        uuid=new QBluetoothUuid(QString("00001101-0000-1000-8000-00805F9B34FB"));
        qDebug()<<"Created socket to "<<adr->toString();

        QObject::connect(socket, SIGNAL(disconnected()), this, SLOT(disconnected()));
        QObject::connect(socket, SIGNAL(connected()), this, SLOT(connected()));
        QObject::connect(socket, SIGNAL(readyRead()), this, SLOT(readSocket()));
        QObject::connect(socket, SIGNAL(error(QBluetoothSocket::SocketError)),
                         this,SLOT(error(QBluetoothSocket::SocketError)));

        socket->connectToService(*adr,
                                 *uuid);


        qDebug() << "ConnecttoService done";
        return address;
    }
    //! Close the socket.
    Q_INVOKABLE bool close()  {
        // Connect to service
        if(!socket) return false;
        socket->close();
        delete socket;
        delete adr;
        delete uuid;
        socket=0;
        return true;
    }
    //! Check to see if the connection is running.
    Q_INVOKABLE bool isConnected() {
        if(!socket) return false;
        if(socket->state()==QBluetoothSocket::ConnectedState
                && apps.length()>0)
            return true;
        return false;
    }
    //! Send an echo, which will get a response.
    Q_INVOKABLE void sendEcho() {
        if(!socket) return;
        char echo[]="Echo!";
        qDebug()<<"Sending an echo.";
        this->cmd(0x00,0x81,strlen(echo)+1,echo);
        return;
    }

    //! List of applications, populated by listApps();
    QList<QString> apps;
    //! Grab the list of running applications.
    Q_INVOKABLE void listApps(){
        char zeroes[1]="";
        if(!socket) return;
        qDebug()<<"Requesting a list of apps.";
        this->cmd(0x00,0x82,1,zeroes); //Requests apps without descriptions.
        return;
    }
    //! Returns the firmware version, if it is known.
    Q_INVOKABLE QString getFirmwareVersion(){
        if(apps.length()>0)
            return apps[0];
        return "Unknown Firmware";
    }

    //! Write a QString to the log.
    Q_INVOKABLE void writelog(QString str){
        log<<str.toAscii().data()<<std::endl;
        qDebug()<<"Logged: "<<str;
    }

private:

    //! Output log stream.
    std::ofstream log;

    //! Open the log file.
    void startLog(){
        if(log.is_open()){
            writelog("WARNING: Tried to double-open the log.");
            return;
        }
        QString date=QDate::currentDate().toString();
        log.open("/home/user/MyDocs/goodfetlog.txt",
                     std::ios_base::out | std::ios_base::app);
        log << "Opening log at " << (char*) date.toAscii().data() <<std::endl;
        log.flush();
    }
    //! Flush the log to disk.
    void flushLog(){
        log.flush();
    }

    //! Set the synchonous mode.
    void setSync(bool sync){
        this->sync=sync;
    }

    qint16 CCregs[256];
    qint32 CCcountdown;

    bool sync;
    bool waiting;
    //! Not yet used.
    QQueue<QByteArray> outbuffer;
    //! Send a GoodFET command.
    void cmd(char app, char verb, qint64 len, char *data){
        char buffer[len+4];
        buffer[0]=app;
        buffer[1]=verb;
        buffer[2]=len&0xFF;
        buffer[3]=(len>>8)&0xFF;
        //qDebug("cmd() Sending 0x%04x bytes of data to App%02x, Verb%02x by cmd().",
        //       (unsigned int) len, app, verb);
        memcpy(buffer+4,data,len&0xFFFF);
        QByteArray b(buffer,(len&0xFFFF)+4);

        if(waiting || !outbuffer.isEmpty()){
            outbuffer.enqueue(b);
            //qDebug("%i packets are now buffered.",outbuffer.length());
        }else{
            waiting=true;
            socket->write(b);
        }
    }
    //! Clear the waiting pool.
    void txWaiting(){
        if(outbuffer.empty()){
            waiting=false;
            return;
        }
        waiting=true;
        socket->write(outbuffer.dequeue());
    }

    //! Send a GoodFET command, writing response to original buffer.  SLOW!
    qint64 synccmd(char app, char verb, qint64 len, char *data){
        cmd(app,verb,len,data);
        return 0;
    }

    //! Handle an incoming packet.
    void handle(char *data){
        char app, verb;
        app=data[0];
        verb=data[1];
        switch(app){
        case 0x00: //MONITOR
            monitorHandle(data);
            break;
        case 0x51: //CCSPI
            ccspiHandle(data);
            break;
        case 0xFF: //DEBUG
            debugHandle(data);
        default:
            handleUnknown(data);
        }
    }

    //! Handle a packet for the MONITOR application.
    void monitorHandle(char *data){
        qint16 len=(data[3]<<8)|data[2];
        switch(data[1]){
        case 0xB1: //CONNECTED
            qDebug()<<"Monitor reports successful connection.";
            break;
        case 0x7F: //RESET NOTIFY
            qDebug("RESET: %s",data+4);
            break;
        case 0x81: //ECHO
            qDebug("ECHO: %s",data+4);
            break;
        case 0x82: //LISTAPPS
            qDebug("LISTAPPS 0x%04x: %s",len,data+4);
            apps<<QString(data+4);
            break;
        default:
            handleUnknown(data);
        }
    }
    //! Handle a debugging message.
    void debugHandle(char *data){
        qint16 len=(data[3]<<8)|data[2];
        switch(data[1]){
        case 0xFF: //DEBUGSTR
            //qDebug()<<"DEBUGSTR: "<<(data+4);
            qDebug()<<"DEBUGSTR: "<<QString(QByteArray(data+4,len));
            break;
        default:
            handleUnknown(data);
        }
    }
    //! Handle a CCSPI message.
    void ccspiHandle(char *data){
        qint16 len=data[2]+(data[3]<<8);

        qint8 r;
        qint16 v;

        switch(data[1]){
        case 0x02: //PEEK
            r=data[4]&~0x40;
            v=(data[5]<<8)|data[6];
            CCregs[r]=v;
            qDebug("Updated r[%02x]=%04x.",r,v);
            break;
        case 0x03: //POKE
            qDebug("Poked a register.");
            break;
        case 0x80: //RX
            if(len>0){
                qDebug("Received a packet of length %i",len );
                QByteArray bytes(data+4,len);
                log<<"CCRXPACKET: "<<bytes.toHex().data()<<std::endl;
                CCinpackets.enqueue(QByteArray(data+4,len));
            }else if(CCcountdown){
                CCcountdown--;
                CCrxpacket(false);
            }
            break;
        case 0x81: //TX
            qDebug("Transmitted a packet.");
            break;

        default:
            handleUnknown(data);
        }
    }

    //! Handle an unknown message.
    void handleUnknown(char *data){
        qDebug("Unknown App=0x%02x, Verb=0x%02x, Len=0x%02x%02x",
               data[0],data[1],
               data[3],data[2]);
    }

    //! Position within the buffer for an incomplete packet.
    qint32 datapos;
    //! Pointer to the next block of data.
    char *nextblock;
#define DATABUFLEN 0x2000
    //! Incoming data buffer, might not be populated.
    char databuf[DATABUFLEN];

    //! Grab data from the serial port, optionally returning the first packet.
    char* nextPacket(bool autohandle=false);

public slots:
    //! Triggered on data arrival.
    void readSocket(){
        nextPacket(true);
    }

    //! Triggered on disconnection.
    void disconnected(){
        qDebug()<<"Disconnected signal fired and caught.";
    }
    //! Triggered on successful connection.
    void connected(){
        qDebug()<<"Connected signal fired and caught.";

        //Ask for the build date and list of applications.
        listApps();
        CCsetup();
    }
    //! Event handler for socket errors.
    void error(QBluetoothSocket::SocketError error){
        qDebug()<<"Caught an error: "<<error<<" "<<socket->errorString();
    }
};

#endif // GOODFET_H
