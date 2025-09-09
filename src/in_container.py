from gear import Gear, GearFQ,POU

class InContainer(GearFQ):
    """Программа для управления приемным бункером.
    
    Приемный бункер измеряет вес, в случае скачкообразного изменения веса вверх происходит оформление приемки материала
    (сколько материала было принято). В остальное время измеряется изменение веса в минуту/между приемками для оценки
    производительности [т/ч]. Грохот управляется ЧП, переполнение грохота контролируется по датчику веса/уровня(пока не ясно)

    Args:
        SFC (_type_): _description_
    """
    raw_m = POU.input(0,hidden=True)
    scrn_m = POU.input(0,hidden=True)
    above_1 = POU.input(False,hidden=True)    #верхнее положение 1 толкателя
    above_2 = POU.input(False,hidden=True)    #верхнее положение 2 толкателя
    hangry = POU.output(False)                #маловато материала
    pusher_1 = POU.output(False,hidden=True)  #первый толкатель
    pusher_2 = POU.output(False,hidden=True)  #второй
    
    push_t = POU.var(int(2),persistent=True)
    push_w = POU.var(int(10),persistent=True)      
    mmax   = POU.var(float(1000),persistent=True)   #номинал тензодатчика
    a      = POU.var(float(1),persistent=True,hidden=True)      #смещение веса
    weight = POU.var(float(0))                      #вес
    msg    = POU.var(str('ОК'))                     #сообщение пользователю
    err    = POU.var(int(0))                        #код ошибки 
    ack    = POU.var(bool(False))
    delta  = POU.var(float(0))
    overload=POU.var(int(0),persistent=True)        #перегруз грохота
    db      =POU.var(int(200),persistent=True)      #определение загрузки
    debet   =POU.var(float(0))                      #счетчик загруженного
    credit  =POU.var(float(0))                      #счетчик потраченного
    performance = POU.var(float(0))                 #производительность в час
    hold    =POU.var(bool(False))
    
    def __init__(self, *, raw_m: int,scrn_m:int, pusher_1:bool , pusher_2:bool , above_1: bool, above_2:bool , fq: int , fault: bool , q: bool , lock: bool | None = None, depends: Gear | None = None, id: str | None = None, parent: POU | None = None) -> None:
        super().__init__(fq=fq, fault=fault, q=q, lock=lock, depends=depends, id=id, parent=parent)
        self.raw_m = raw_m
        self.scrn_m = scrn_m
        self.pusher_1 = pusher_1
        self.pusher_2 = pusher_2
        self.above_1 = above_1
        self.above_2 = above_2
        self.subtasks += (self.monitor, )
        self.exec(self._offset())
        self.exec(self._balance())
        
    def monitor(self):
        self.weight = self.raw_m/65535*self.mmax + self.a 

        if self.scrn_m>=self.overload*655.35 and self.q and not self.hold:
            self.hold = True
            if self.fq!=self.sp:
                self.sp = self.fq
            self.fq = 0
            self.msg = 'ПАУЗА'
            
        if self.scrn_m+655<=self.overload*655.35 and self.q and self.hold:
            self.hold = False
            self.fq = self.sp
            self.msg = 'РАБОТА'

    def _balance(self):
        while True:
            m = self.weight
            yield from self.until(lambda: m+self.db<self.weight,max=5000)
            dm = self.weight - m
            if dm>0: 
                self.debet+=dm
            else:
                self.credit-=dm

    def _performance(self):
        performance=[ ]
        while self.q:   #пока работаем
            m0 = self.credit
            yield from self.pause(60000)
            m1 = self.credit
            performance.append( (m1-m0)*60 )    #производительность кг/час
            if len(performance)>60:
                performance.pop(0)
            self.performance = sum(performance)/len(performance)
        
    def _offset(self):
        while not self.q:
            yield from self.till(lambda: self.delta == 0 )
            yield from self.pause(2000)
            self.a += self.delta
            self.delta = 0 

    def _push(self, pusher: int):
        T = 0
        self.pusher_1 = pusher == 1
        self.pusher_2 = pusher == 2
        while T<self.push_t:
            yield from self.pause(1000)
            T+= 1

        ntry = 2
        while ntry>0 and ((pusher==1 and not self.above_1) or (pusher==2 and not self.above_2)) :
            self.pusher_1 = False
            self.pusher_2 = False
            yield from self.until(lambda: self.above_1 and self.above_2,max=4000)
            self.pusher_1 = not self.above_1 and pusher==1   #если толкатель не вернулся, то еще раз его толкнем 
            self.pusher_2 = not self.above_2 and pusher==2
            yield from self.pause(1000)
            ntry-=1
        
        if ntry==0:
            self.msg = f'ПРОВЕРЬ ТОЛКАТЕЛЬ#{pusher}!'
            self.err = 100+pusher
            self.ack = False
            yield from self.until(lambda: self.ack)
        else:
            T = 0
            self.pusher_1 = False
            self.pusher_2 = False
            while T<self.push_w+self.push_t:
                yield from self.pause(1000)
                T += 1
        
    def _pushers(self):
        while True:
            if not self.hold:
                yield from self._push(1)
                yield from self._push(2)
            else:
                yield from self.pause(10000)    #10 сек спим
            yield
        
    def _test(self, on: bool):
        if on:
            if self.rsn==0:
                self.inspect( fault = lambda x: x.force( True if self._pass==0 else None ) )
            elif self.rsn==1:   #приход
                self.inspect( raw_m = lambda x: x.force( self.raw_m + self.db/2/self.mmax*65535 ) )
            elif self.rsn==2:   #расход
                self.inspect( raw_m = lambda x: x.force( self.raw_m - self.db/10/self.mmax*65535) )
            elif self.rsn==3:   #перегрузка/завал
                self.inspect( scrn_m = lambda x: x.force( self.overload/100*65535 if self._pass==0 else None) )
        else:
            self._pass = (self._pass + 1) % 2

    def _begin(self):
        self.msg = 'РАБОТА'
        self.pushers = self.exec(self._pushers())
        self.exec(self._performance())
    
    def _end(self):
        self.msg = 'ОТДЫХАЮ'
        self.pushers.close()
        self.exec(self._offset())   #во время работы смещение не работает