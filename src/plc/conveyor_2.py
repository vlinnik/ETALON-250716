from gear import Gear, GearFQ, TOF,TRIG
from pyplc.pou import POU

class ConveyorFQ(GearFQ):
    rotating = POU.var(False)
    rot = POU.input(False, hidden = True)
    
    def __init__(self,*,rot: bool|None = None, fq: int | None = None, fault: bool | None = None, q: bool | None = None, lock: bool | None = None, depends: Gear | None = None, id: str | None = None, parent: POU | None = None) -> None:
        super().__init__(fq=fq, fault=fault, q=q, lock=lock, depends=depends, id=id, parent=parent)
        self.rot = rot
        self._rotating = TOF(clk = TRIG(clk = lambda: self.rot), pt=10000, q = self.monitor)
        self.subtasks += (self._rotating, )
    
    def monitor(self, rot: bool):
        self.rotating = rot
        if not rot and self.q:
            self.ok = False
            self.log('ошибка: нет вращения')
