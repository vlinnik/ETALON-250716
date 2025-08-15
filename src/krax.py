#Ниже идет Ваша программа
from pyplc.platform import plc,plc as hw
from pyplc.utils.misc import TOF,TON
from in_container import InContainer
from gear import GearROT as Noria, GearROT as Conveyor, GearFQ as Siever, GearFQ as Drum, GearFQ as Exhauser, GearChain
from sys import platform
from collections import namedtuple

if platform == 'vscode': # never realy used, only for auto-completion
    PLC = namedtuple('PLC', ['IN_CONT_M_1','VIB_SCRN_M_1','VIB_SIEVE_M_9','DRUM_T_5A','DRUM_T_5B','DRUM_T_5C','FILTER_P_9','VIBR_FQ_1','FEED_FQ_2','DRUM_FQ_5','FILTER_FQ_8','SIEVE_FQ_9','EMERGENCY_2','EMERGENCY_3','EMERGENCY_4','EMERGENCY_5','EMERGENCY_6','EMERGENCY_7','FEED_ROT_2','FEED_ROT_3','FEED_ROT_4','FEED_ROT_6','NORI_ROT_7','PUSHER_ON_BOT_1A','PUSHER_ON_BOT_1B','PUSHER_ON_TOP_1A','PUSHER_ON_TOP_1B','NORI_TORN_7','FAULT_FQ_1','FAULT_FQ_2','FAULT_FQ_5','FAULT_FQ_8','FAULT_FQ_9','FEED_ISON_3','FEED_ISON_4','FEED_ISON_6','PUSHER_ON_1A','PUSHER_ON_1B','FQ_EN_1','FQ_EN_2','FEED_ON_3','FEED_ON_4','FQ_EN_5','FEED_ON_6','NORI_ON_7','FILTER_EN_8','SIEVE_EN_9','UNLOAD_OPEN_8A','UNLOAD_OPEN_8B'])
    hw = PLC()

siever = Siever( q = hw.SIEVE_EN_9, fq = hw.SIEVE_FQ_9,fault = hw.FAULT_FQ_9 )
exhauser = Exhauser( fq = hw.FILTER_FQ_8, fault = hw.FAULT_FQ_8, q = hw.FILTER_EN_8)
noria = Noria(rot = hw.NORI_ROT_7, fault = lambda: hw.NORI_TORN_7 or hw.EMERGENCY_7, q = hw.NORI_ON_7, lock=~TON(clk = lambda: siever.rdy,pt=2000) )
conveyor_6 = Conveyor( rot = hw.FEED_ROT_6, fault = lambda: hw.EMERGENCY_6, q = hw.FEED_ON_6, lock=~TON(clk = lambda: noria.rdy,pt=2000) )
drum_5 = Drum( fq = hw.DRUM_FQ_5, fault = lambda: hw.FAULT_FQ_5 or hw.EMERGENCY_5, q = hw.FQ_EN_5)
conveyor_4 = Conveyor( rot = hw.FEED_ROT_4, fault = lambda: hw.EMERGENCY_4, q = hw.FEED_ON_4, lock=~TON(clk = lambda: drum_5.rdy,pt=2000) )
conveyor_3 = Conveyor( rot = hw.FEED_ROT_3, fault = lambda: hw.EMERGENCY_3, q = hw.FEED_ON_3, lock=~TON(clk = lambda: conveyor_4.rdy,pt=2000) )
conveyor_2 = Conveyor( rot = hw.FEED_ROT_2, fault=lambda: hw.EMERGENCY_2 or hw.FAULT_FQ_2, q = hw.FQ_EN_2,lock=~TON(clk = lambda: conveyor_3.rdy,pt=2000) )

in_container = InContainer(raw_m = hw.IN_CONT_M_1, en = hw.FQ_EN_1, fq = hw.VIBR_FQ_1, pusher_1 = hw.PUSHER_ON_1A, pusher_2 = hw.PUSHER_ON_1B, above_1 = hw.PUSHER_ON_TOP_1A, above_2 = hw.PUSHER_ON_TOP_1B)

factory = GearChain( gears=( siever, noria,conveyor_6 , conveyor_4, conveyor_3, conveyor_2 ) )

instances = (in_container, siever, exhauser, noria, conveyor_6,drum_5,conveyor_4, conveyor_3,conveyor_2, factory)

if platform == 'linux':
    from imitation import IValveOrCylinder,IRotation
    ipusher_1 = IValveOrCylinder(open=hw.PUSHER_ON_1A, closed=hw.PUSHER_ON_TOP_1A)
    ipusher_2 = IValveOrCylinder(open=hw.PUSHER_ON_1B, closed=hw.PUSHER_ON_TOP_1B)
    irot_7    = IRotation(q = hw.NORI_ON_7, rot = hw.NORI_ROT_7 )
    irot_6    = IRotation(q = hw.FEED_ON_6, rot = hw.FEED_ROT_6 )
    irot_4    = IRotation(q = hw.FEED_ON_4, rot = hw.FEED_ROT_4 )
    irot_3    = IRotation(q = hw.FEED_ON_3, rot = hw.FEED_ROT_3 )
    irot_2    = IRotation(q = hw.FQ_EN_2, rot = hw.FEED_ROT_2 )
    
    instances += (ipusher_1, ipusher_2, irot_7,irot_6,irot_4, irot_3,irot_2) 
    

plc.run( instances=instances, ctx=globals() )
