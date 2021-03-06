import sys
sys.path.append(r'../..')

from marketsim import (strategy, trader, orderbook, order, timeserie,
                       scheduler, types, observable, veusz, mathutils)


from common import expose, Constant

@expose("Fundamental value", __name__)
def FundamentalValue(ctx):
    
    ctx.volumeStep = 30
    fv = 200

    demo = ctx.addGraph('demo')
    myVolume = lambda: [(observable.VolumeTraded(), demo)]
    myPrice = lambda: [(observable.Price(orderbook.OfTrader()), demo)]

    return [
        ctx.makeTrader_A( 
            strategy.LiquidityProvider(
                 volumeDistr=mathutils.constant(6),
                 orderFactoryT=order.WithExpiryFactory(
                     expirationDistr=mathutils.constant(10))),
            "liquidity"),
    
        ctx.makeTrader_A( 
            strategy.FundamentalValue(
               fundamentalValue = mathutils.constant(fv),
               creationIntervalDistr = mathutils.constant(1.),
               volumeDistr = mathutils.constant(1)), 
            "fv_200", 
            myVolume() + myPrice() + Constant(fv, demo)),

        ctx.makeTrader_A(
            strategy.FundamentalValueEx(
               fundamentalValue = mathutils.constant(fv),
               creationIntervalDistr = mathutils.constant(1.),
               volumeDistr = mathutils.constant(1)), 
            "fv_ex_200", 
            myVolume())
    ]

