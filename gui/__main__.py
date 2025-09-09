import sys
from pysca import app
from pysca.device import PYPLC
import pygui.navbar as navbar
from AnyQt.QtCore import QUrl
from AnyQt.QtWidgets import QWidget
from AnyQt.QtWebEngineWidgets import QWebEngineView
from pysca.helpers import user_window
from pysca.bindable import Property

from .gears import GearFQ,GearROT,NORIA,SIEVER,DRUM,EXHAUSER,INCONTAINER

Siever: SIEVER
Noria: NORIA
Conv6: GearROT
Conv4: GearROT
Conv3: GearROT
Drum: DRUM
Exhauser: EXHAUSER
Conv2: GearFQ
InContainer: GearFQ


class DASHBOARD( user_window( 'ui/Dashboard.ui',QWidget ) ):
    webEngineView : QWebEngineView
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None, url: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            self.setWindowTitle(title)
            
        if url is not None:
            self.webEngineView.setUrl(QUrl(url))


def main():
    global Home,Siever,Noria,Conv6,Conv4,Conv3,Drum,Exhauser,Conv2,InContainer
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='127.0.0.1', help='IP address of the device')
    args.add_argument('--simulator', action='store_true', default=False, help='Same as --device 127.0.0.1')
    ns = args.parse_known_args()[0]
    if ns.simulator:
        ns.device = '127.0.0.1'
        import subprocess
        logic = subprocess.Popen(["python3", "src/krax.py"])
    
    dev = PYPLC(ns.device)
    app.devices['PLC'] = dev
    
    Home = app.window('ui/Home.ui')
    Siever = SIEVER(Home,title='Вибро-сито (9)')
    Noria = NORIA(Home,title='Нория (7)')
    Conv6 = GearROT(Home,title='Питатель (6)',prefix='CONVEYOR_6',rot='FEED_ROT_6')
    Drum  = DRUM(Home,title='Сушильный барабан (5)')
    Conv4 = GearROT(Home,title='Питатель (4)',prefix='CONVEYOR_4',rot='FEED_ROT_4')
    Conv3 = GearROT(Home,title='Питатель (3)',prefix='CONVEYOR_3',rot='FEED_ROT_3')
    Exhauser = EXHAUSER(Home,title='Батарейный фильтр (8)')
    Conv2 = GearFQ(Home,title='Питатель (2)', prefix='CONVEYOR_2',en='FQ_EN_2')
    InContainer = INCONTAINER(Home,title='Приемный (1)',en='FQ_EN_1')
    # с использованием navbar
    navbar.append(Home)       
    navbar.append(DASHBOARD(title='Пуск'))
    navbar.append(DASHBOARD(title='Работа',url='http://localhost:3000/d/a0819563-8b3a-41fd-b0c7-20a11ed09d68/rabota?orgId=1&refresh=5s&kiosk'))
    navbar.instance.setWindowTitle('АСУ ИННЕРЕ-250716 (c) 2025, ООО "ЭТАЛОН-КОМ"')
    navbar.instance.show( )
    # или 
    # Home.show()               
    
    dev.start(100)
    app.start( ctx = globals() )
    dev.stop( )

    if ns.simulator:
        logic.terminate( )
        pass

if __name__=='__main__':
    main( )
    