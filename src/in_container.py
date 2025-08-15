from pyplc.sfc import SFC,POU

class InContainer(SFC):
    """Программа для управления приемным бункером.
    
    Приемный бункер измеряет вес, в случае скачкообразного изменения веса вверх происходит оформление приемки материала
    (сколько материала было принято). В остальное время измеряется изменение веса в минуту/между приемками для оценки
    производительности [т/ч]. Грохот управляется ЧП, переполнение грохота контролируется по датчику веса/уровня(пока не ясно)

    Args:
        SFC (_type_): _description_
    """
    raw_m = POU.input(0,hidden=True)
    en = POU.output(False,hidden=True)
    fq = POU.output(int(0), hidden=True)
    overload = POU.input(False,hidden=True)    
    hangry = POU.output(False,hidden=True)      #маловато материала
    pusher_1 = POU.output(False,hidden=True)  #первый толкатель
    pusher_2 = POU.output(False,hidden=True)  #второй
    above_1 = POU.input(False,hidden=True)  #верхнее положение 1 толкателя
    above_2 = POU.input(False,hidden=True)  #верхнее положение 2 толкателя
    lock = POU.input(False,hidden=True)
    
    push_t = POU.var(int(10))
    push_w = POU.var(int(1))
    
    def __init__(self, *, raw_m: int, lock: bool | None = None, en: bool | None = None, fq: int | None = None, pusher_1:bool = None, pusher_2:bool = None, above_1: bool=None, above_2:bool=None , id: str | None = None, parent: POU | None = None):
        super().__init__(id=id, parent=parent)
        self.raw_m = raw_m
        self.en = en 
        self.fq = fq 
        self.lock = lock
        self.pusher_1 = pusher_1
        self.pusher_2 = pusher_2
        self.above_1 = above_1
        self.above_2 = above_2
        self.exec(self.pushers())
        
    def push(self, pusher: int):
        if not self.en:
            yield
            return
        T = 0
        while T<self.push_t:
            T+= 1
            yield from self.pause(1000)
        self.pusher_1 = pusher == 1
        self.pusher_2 = pusher == 2
        T = 0
        while T<self.push_w:
            T += 1
            yield from self.pause(1000)
        self.pusher_1 = False
        self.pusher_2 = False
        yield from self.until(lambda: self.above_1 and self.above_2)
        
    def pushers(self):
        while True:
            yield from self.push(1)
            yield from self.push(2)
        
    def main(self):
        self.log('приемный бункер готов к работе')
        while True:
            if self.lock and self.en:
                self.en = False
            yield
        self.log('приемный бункер остановлен')
