from marketsim import scheduler, order, mathutils, types, registry   
from _basic import Strategy
from _two_sides import TwoSides
from _generic import Generic, randomSide
from _wrap import wrapper2
from marketsim.types import *

class _Noise_Impl(TwoSides):
    
    def __init__(self):
        self._eventGen = scheduler.Timer(self.creationIntervalDistr)
        TwoSides.__init__(self)
        
    def _orderFunc(self):
        conv = types.Side.byId
        return (types.Side.byId(self.sideDistr()), (int(self.volumeDistr()),)) 

exec wrapper2("Noise", 
             """ Noise strategy is a quite dummy strategy that randomly creates an order 
                 and sends it to the order book. 
                 
                 It has following parameters:

                 |orderFactoryT| 
                     order factory function (default: order.Market.T)

                 |creationIntervalDistr| 
                     defines intervals of time between order creation 
                     (default: exponential distribution with |lambda| = 1)
                     
                 |sideDistr| 
                     side of orders to create 
                     (default: discrete uniform distribution P(Sell)=P(Buy)=.5)
             """,
             [("orderFactory",          "order.MarketFactory",          'Side -> Volume -> IOrder'),
              ("sideDistr",             "mathutils.rnd.randint(0,1)",   "() -> int"), # in fact it should be () -> Side
              ("volumeDistr",           "mathutils.rnd.expovariate(1.)",'() -> Volume'),
              ("creationIntervalDistr", "mathutils.rnd.expovariate(1.)",'() -> TimeInterval')])

@registry.expose(["Generic", "Noise"], args = ())
def NoiseEx     (orderFactory           = order.MarketFactory,
                 sideDistr              = randomSide, 
                 volumeDistr            = mathutils.rnd.expovariate(1.), 
                 creationIntervalDistr  = mathutils.rnd.expovariate(1.)):
    
    r = Generic(orderFactory = orderFactory, 
                eventGen     = scheduler.Timer(creationIntervalDistr), 
                sideFunc     = sideDistr, 
                volumeFunc   = volumeDistr)
    
    return r
    