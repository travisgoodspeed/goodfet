#include <QtGui/QApplication>
#include <QtDeclarative/QDeclarativeView>
#include <QtDeclarative/QDeclarativeContext>
#include "qmlapplicationviewer.h"

#include "goodfet.h"

GoodFET *gf;

Q_DECL_EXPORT int main(int argc, char *argv[])
{
    QApplication *app=new QApplication(argc,argv);
    QmlApplicationViewer *viewer=new QmlApplicationViewer();
    gf=new GoodFET();

    viewer->rootContext()->setContextProperty("GoodFET",gf);
    viewer->setOrientation(QmlApplicationViewer::ScreenOrientationLockPortrait);
    viewer->setMainQmlFile(QLatin1String("qml/meegoodfet/main.qml"));


    viewer->showExpanded();
    return app->exec();
}
