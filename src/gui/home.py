from qtpy.QtWidgets import QWidget,QLabel,QAction
from pysca import app

class Home(QWidget):
    def __init__(self,/, parent: QWidget | None = None, *_ ) -> None:
        super().__init__( parent )
        self.iconTotal: QLabel
        self.actionReset: QAction

    def setupUi(self):
        self.iconTotal.addActions( [self.actionReset] )
        
    def on_actionReset_triggered(self):
        app.ctx['IN_CONTAINER_DEBET'] = 0.0