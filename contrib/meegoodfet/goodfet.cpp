#include "goodfet.h"


GoodFET::GoodFET(QObject *parent) :
    QObject(parent)
{
    startLog();
    nextblock=databuf;
    sync=false;
    waiting=false;
}

char* GoodFET::nextPacket(bool autohandle){
    qint64 len=0;
    if (!socket)
        return 0;

    //socket->waitForBytesWritten(1024);
    //qDebug()<<"Reading data.";


    len=socket->read(nextblock+datapos,1024);
    datapos+=len;

    //qDebug()<<"Read "<<datapos<<"/"<<(((nextblock[3]<<8)|nextblock[2])+4)<<" bytes of data, total";


    //If in synchronous mode, we need even more data.
    while((!autohandle) && ((((nextblock[3]<<8)|nextblock[2])+4)>datapos)){
        //qDebug()<<"Spinning, waiting on more of the packet.";
        len=socket->read(nextblock+datapos,256);
        datapos+=len;
    }


    //We don't have all of the block, so return and wait for next callback.
    if(autohandle && ((((nextblock[3]<<8)|nextblock[2])+4)>datapos)){
        return 0;
    }

    //Fix things if we've overrun the buffer.
    while((((nextblock[3]<<8)|nextblock[2])+4)<datapos){
        handle(nextblock);
        datapos-=(((nextblock[3]<<8)|nextblock[2])+4);
        nextblock+=(((nextblock[3]<<8)|nextblock[2])+4);
    }

    //We've finished the packet evenly, move back to [0].
    if((((nextblock[3]<<8)|nextblock[2])+4)==datapos  // Proper conclusion of last packet in sequence, or
            || (databuf-nextblock>(DATABUFLEN>>1))    // About to overflow the buffer.
            ){
        handle(nextblock);
        datapos=0;
        nextblock=databuf;

        //Finally, mark that there are no more expected bytes and we can transmit.
        waiting=false;
        txWaiting();
    }
    return 0;
}
