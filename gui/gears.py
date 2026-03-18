from qtpy.QtWidgets import QWidget,QDialog,QLabel,QPushButton
from qtpy.QtGui import QCloseEvent,QShowEvent
from qtpy.QtCore import QSettings,QPoint
from pysca.helpers import user_window
from typing import cast,Optional

class GearBase( QDialog ):
    name: QLabel    
    def __init__(self, parent: QWidget|None = None, *args,  **kwargs):
        super().__init__(parent, *args)
            
    def setupUi(self,*args,title: Optional[str]=None , **kwargs):
        if title is not None:
            cast(QLabel,self.name).setText(title)

GearFQ = GearBase
GearROT= GearBase
NORIA = GearBase
SIEVER = GearBase
DRUM = GearBase
EXHAUSER = GearBase
INCONTAINER = GearBase
