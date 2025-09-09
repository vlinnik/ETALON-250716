from AnyQt.QtWidgets import QWidget,QDialog,QLabel,QPushButton
from AnyQt.QtGui import QCloseEvent,QShowEvent
from AnyQt.QtCore import QSettings,QPoint
from pysca.helpers import user_window
from typing import cast

class GearFQ( user_window( 'ui/GearFQ.ui',QDialog ) ):
    name: QLabel    
    test_fault: QPushButton
    test_lock: QPushButton
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)
            
    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

    def on_test_lock_pressed(self):
        self.test_lock.setProperty('rsn',1)

class GearROT( user_window( 'ui/GearROT.ui',QDialog ) ):
    name: QLabel
    test_fault: QPushButton
    test_lock: QPushButton
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)

    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

    def on_test_lock_pressed(self):
        self.test_lock.setProperty('rsn',1)

class NORIA( user_window( 'ui/GearNORI.ui',QDialog ) ):
    name: QLabel
    test_fault: QPushButton
    test_lock: QPushButton
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)

    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

    def on_test_lock_pressed(self):
        self.test_lock.setProperty('rsn',1)

class SIEVER( user_window( 'ui/SIEVER.ui',QDialog ) ):
    name: QLabel
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)
                    
    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

class DRUM( user_window( 'ui/DRUM.ui',QDialog ) ):
    name: QLabel
    test_fault: QPushButton
    test_lock: QPushButton
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)

    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

    def on_test_lock_pressed(self):
        self.test_lock.setProperty('rsn',1)

    def on_test_t_pressed(self):
        self.test_t.setProperty('rsn',2)

class EXHAUSER( user_window( 'ui/EXHAUSER.ui',QDialog ) ):
    name: QLabel
    test_fault: QPushButton
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)

    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

class INCONTAINER( user_window( 'ui/INCONTAINER.ui',QDialog ) ):
    name: QLabel
    test_fault: QPushButton
    test_income: QPushButton
    test_overload: QPushButton
    
    def __init__(self, parent: QWidget|None = None, *args, title: str|None=None , **kwargs):
        super().__init__(parent, *args, **kwargs)
        if title is not None:
            cast(QLabel,self.name).setText(title)

    def on_test_fault_pressed(self):
        self.test_fault.setProperty('rsn',0)

    def on_test_income_pressed(self):
        self.test_income.setProperty('rsn',1)

    def on_test_outcome_pressed(self):
        self.test_overload.setProperty('rsn',2)

    def on_test_overload_pressed(self):
        self.test_overload.setProperty('rsn',3)

