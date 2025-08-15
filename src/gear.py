from pyplc.sfc import SFC,POU
from pyplc.utils.latch import RS
from pyplc.utils.trig import TRIG,FTRIG,RTRIG
from pyplc.utils.misc import TOF

class Gear(SFC):
    """Базовый класс для конвейеров, норий, сита, барабана"""
    IDLE = 0
    STARTUP = 1
    RUN = 2
    STOP = 3
    
    rdy = POU.var(False)
    on  = POU.var(False)
    off = POU.var(False)
    lock = POU.var(False)
    startup_t = POU.var(int(5),persistent=True)
    
    fault = POU.input(False, hidden = True)
    _lock = POU.input(False,hidden = True)
    q   = POU.output(False, hidden = True)    
    
    def __init__(self, fault: bool=None, q: bool = None, lock: bool = None, id: str = None, parent: POU = None) -> None:
        super().__init__(id, parent)
        self.state = Gear.IDLE
        self.ok = True
        self.fault = fault
        self._lock = lock
        self.q = q
        self._ctl = RS(reset = lambda: self.off, set = lambda: self.on, q = self.control )
        self.subtasks = (self._ctl, )
    
    def _turnon(self):
        self.ok = True
    
    def _turnoff(self):
        self.ok = False
    
    def control(self,power: bool):
        self.q = power and not self._lock
        if power and self._lock:
            self.lock = True
        if not power:
            self.lock = False
            self.ok = True
        
    def main(self):
        self.state = Gear.IDLE
        self.rdy = False
        self.busy = False
        yield from self.until( lambda: self.q,step='ожидаем запуска' )
        
        self.state = Gear.STARTUP
        self._turnon( )
        self.log('разгоняемся')
        T = 0 
        while T<self.startup_t and not self.fault and self.ok and not self._lock:
            yield from self.pause(1000)
            T+=1
            self.rdy = not self.rdy
        self.rdy = True

        self.state = Gear.RUN        
        self.log('вышли в режим')
        yield from self.till(lambda: self.q and not self.fault and self.ok and not self._lock, step = 'в работе')
        self.state = Gear.STOP
        self.busy = False
        self.rdy = False
        self._turnoff( )
        if self._lock: 
            self.log('отключение по блокировке')
            self.lock = True
        
        if self.q:
            if self.fault:
                self.log('аварийный останов')
            
        self.q = False

class GearROT(Gear):
    rotating = POU.var(False)
    rot = POU.input(False, hidden = True)
    
    def __init__(self, fault: bool = None, q: bool = None, lock: bool = None, rot: bool = None, id: str = None, parent: POU = None) -> None:
        super().__init__(fault=fault, q=q, lock=lock, id=id, parent=parent)
        self.rot = rot
        self._rotating = TOF(clk = TRIG(clk = lambda: self.rot), q = self.monitor)
        self.subtasks += (self._rotating, )

    def monitor(self, rot: bool):
        self.rotating = rot
        if not rot and self.q:
            self.ok = False
            self.log('ошибка: нет вращения')

class GearFQ(Gear):
    """Базовый класс для конвейеров c ЧП, сита, барабана с частотным управлением"""
    fq = POU.output(False, hidden = True)
    sp = POU.var(int(32767), persistent=True)  #пусковая частота
    
    def _turnon(self):
        self.fq = self.sp
        
    def _turnoff(self):
        self.fq = 0
    
    def __init__(self, fq: bool = None,  fault: bool = None, q: bool = None, lock: bool = None, rot: bool = None, id: str = None, parent: POU = None) -> None:
        super().__init__(fault=fault, q=q, lock=lock, id=id, parent=parent)
        self.fq = fq

class GearChain(SFC):
    IDLE = 0
    STARTING = 1
    STOPPING = 2
    UNDEFINED = 3
    
    on  = POU.var(False)
    off = POU.var(False)
    msg = POU.var('ГОТОВ')

    def __init__(self, gears: tuple[Gear], id: str = None, parent: POU = None) -> None:
        super().__init__( id=id, parent=parent)
        self.gears = gears
        self._t_on = FTRIG(clk = lambda: self.on )
        self._t_off= RTRIG(clk = lambda: self.off )
        self.subtasks = (self._t_on, self._t_off )
        self.state = GearChain.IDLE
            
    def _start(self):
        self.state = GearChain.STARTING
        for gear in self.gears:
            if gear.state == Gear.RUN:
                continue
            self.msg=f'ПУСК {gear.id}'
            if gear.lock:
                gear.off = True
                yield
                gear.off = False
            gear.on = True
            yield
            gear.on = False
            yield from self.till(lambda: gear.state != Gear.RUN and self.state == GearChain.STARTING, max=gear.startup_t*1000+1000, step=f'ожидаем запуска {gear.id}')
            if gear.state!= Gear.RUN:
                self.msg=f'ПРОВЕРЬ {gear.id}'
                self.log(f'неудачная попытка запуска {gear.id}')
                return
            if self.state != GearChain.STARTING:
                break
            yield from self.pause(2000)
        if self.state==GearChain.STARTING: 
            self.state = GearChain.IDLE
            self.msg = 'ГОТОВ'
    
    def _stop(self):
        self.state = GearChain.STOPPING
        for gear in reversed(self.gears):
            if gear.state == Gear.IDLE:
                continue
            self.msg=f'РАЗГРУЗКА {gear.id}'
            yield from self.till(lambda: gear.state == Gear.RUN and self.state==GearChain.STOPPING, max = gear.startup_t*1000, step = f'штатный останов {gear.id}')
            gear.off = True
            yield
            gear.off = False
            self.msg=f'ОСТАНОВ {gear.id}'
            yield from self.till(lambda: gear.state != Gear.IDLE and self.state==GearChain.STOPPING, step=f'ожидаем остановки {gear.id}',max = 2000)
            if gear.state != Gear.IDLE:
                self.msg=f'ПРОВЕРЬ {gear.id}'
                self.log(f'неудачная попытка остановки {gear.id}')
                return
            if self.state != GearChain.STOPPING:break
            yield from self.pause(2000)
        if self.state==GearChain.STOPPING: 
            self.state = GearChain.IDLE
            self.msg = 'ГОТОВ'

    def main(self):
        yield from self.until(lambda: self._t_on.q or self._t_off.q, step='ожидаем пуск/стоп')
        
        if self._t_on.q:
            if self.state!=GearChain.STARTING:
                self.log('последовательный запуск')
                self.exec(self._start())
            else:
                self.state=GearChain.IDLE
        if self._t_off.q:
            if self.state!=GearChain.STOPPING:
                self.log('последовательная остановка')
                self.exec(self._stop() )
            else:
                self.state=GearChain.IDLE
        
        
    
    