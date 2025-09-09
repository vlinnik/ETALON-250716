from gear import GearFQ,POU

class PID:
    def __init__(self, Kp, Ki, Kd, sp:int=0, limits=(None, None)):
        self.Kp = Kp  # Пропорциональный коэффициент
        self.Ki = Ki  # Интегральный коэффициент
        self.Kd = Kd  # Дифференциальный коэффициент

        self.sp = sp
        self.limits = limits  # (min, max)

        self._last_error = 0.0
        self._integral = 0.0
        self._last_time = None

    def setup(self, Kp, Ki, Kd):
        self.Kp = Kp  # Пропорциональный коэффициент
        if self.Ki!=Ki and Ki!=0:
            self._integral = self._integral / Ki *self.Ki
        self.Ki = Ki  # Интегральный коэффициент
        self.Kd = Kd  # Дифференциальный коэффициент

    def reset(self):
        self._last_error = 0
        self._integral = 0
        self._initialized = False

    def compute(self, sp:int, pv:int, dt:int=100):
        self.sp = sp
        error = sp - pv
        derivative = 0.0

        if self._initialized:
            if dt > 0:
                derivative = (error - self._last_error) / dt/1000
                self._integral += error * dt/1000

        output = (
            self.Kp * error +
            self.Ki * self._integral +
            self.Kd * derivative
        )

        # Ограничение выходного сигнала
        min_out, max_out = self.limits
        if min_out is not None:
            output = max(min_out, output)
        if max_out is not None:
            output = min(max_out, output)

        # Обновление состояния
        self._last_error = error
        self._initialized = True

        return int(output)


class Exhauser(GearFQ):
    w_1 = POU.var(int(10),persistent=True)  #для интерфейса оператора целевые значения для температур
    p_1 = POU.var(int(3),persistent=True)
    
    w_2 = POU.var(int(10),persistent=True)
    p_2 = POU.var(int(3),persistent=True)
    
    kp  = POU.var(float(0.5),persistent=True)
    ki  = POU.var(float(0.1),persistent=True)
    kd  = POU.var(float(0.0),persistent=True)
    
    target    = POU.var(int(0))                 #необходимое разряжение
    pressure  = POU.input(int(0),hidden=True)   #текущее разряжение
    
    elapsed_1 = POU.var(int(0))
    elapsed_2 = POU.var(int(0))
    
    open_1 = POU.output(False,hidden=True)
    open_2 = POU.output(False,hidden=True)
    
    def __init__(self, pressure: int|None = None,open_1:bool|None = None,open_2:bool|None=None, fq: int|None = None, fault: bool|None = None, q: bool|None = None, lock: bool|None = None,  id: str|None = None, parent: POU|None = None) -> None:
        super().__init__(fq, fault, q, lock, id=id, parent=parent)
        self.open_1 = open_1
        self.open_2 = open_2
        self.pressure = pressure
        self.cleaner = None
        self.work = None
        self.pid = PID(self.kp,self.ki,self.kd,limits=(0,65535))
        
    def _begin(self):
        self.target = self.pressure
        self.cleaner = self.exec(self._cleaner())
        self.work = self.exec(self._working())
        
    def _end(self):
        self.cleaner.close( )
        self.work.close( )
    
    def _working(self):
        self.log('starting exhauser pressure stabilization')
        self.pid.reset( )
        while True:
            self.pid.setup(self.kp,self.ki,self.kd)
            self.fq = self.pid.compute(self.target, self.pressure, 100 )
            yield
            
    def _cleaner(self):
        self.log('starting exhauser auto clean')
        T0 = 0 
        T1 = 0
        while True:
            yield from self.pause(1000)
            T0 += 1
            T1 += 1
            self.elapsed_1 = self.w_1 - T0
            self.elapsed_2 = self.w_2 - T1
            self.open_1 = self.elapsed_1<self.p_1
            self.open_2 = self.elapsed_2<self.p_2
            if T0>=self.w_1:
                T0 = 0 
            if T1>=self.w_2:
                T1 = 0