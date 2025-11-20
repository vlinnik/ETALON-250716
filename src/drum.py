from gear import GearFQ,POU
from typing import Callable,Union

class Drum(GearFQ):
    t_in = POU.var(int(32767),persistent=True)  #для интерфейса оператора целевые значения для температур
    t_out= POU.var(int(32767),persistent=True)
    t_air= POU.var(int(32767),persistent=True)
    
    t_5a = POU.input(int(0),hidden=True)
    t_5b = POU.input(int(0),hidden=True)
    t_5c = POU.input(int(0),hidden=True)
    
    def __init__(self, rot: Union[ bool,Callable[[],bool] ],t_5a: int|None = None,t_5b: int|None = None,t_5c: int|None = None, fq: int|None = None, fault: bool|None = None, q: bool|None = None, lock: bool|None = None,  id: str|None = None, parent: POU|None = None) -> None:
        super().__init__(rot=rot,fq=fq, fault=fault, q=q, lock=lock, id=id, parent=parent)
        self.t_5a = t_5a
        self.t_5b = t_5b
        self.t_5c = t_5c
        
    def _test(self, on: bool):
        super()._test( on )
        if on:
            if self.rsn==2:
                self.inspect( t_5a = lambda x: x.force( self.t_in  ),
                            t_5b = lambda x: x.force( self.t_out ),
                            t_5c = lambda x: x.force( self.t_air ))
        