import sys
sys.path.append(r'../..')

from marketsim import strategy, orderbook, trader, scheduler, observable, veusz, mathutils, timeserie
from common import expose

@expose("Arbitrage", __name__)
def Arbitrage(ctx):

    liqVol = mathutils.product(mathutils.rnd.expovariate(.1), mathutils.constant(2))
    
    ctx.volumeStep = 70

    return [
        ctx.makeTrader_A( 
            strategy.LiquidityProvider(defaultValue=50., volumeDistr=liqVol), 
            "LiquidityProvider_A"),
    
        ctx.makeTrader_B( 
            strategy.LiquidityProvider(defaultValue=150., volumeDistr=liqVol), 
            "LiquidityProvider_B"),
            
        ctx.makeMultiAssetTrader([ctx.remote_A, ctx.remote_B], strategy.Arbitrage(), "Arbitrager")
    ]    

    
"""
from marketsim import trader, strategy, orderbook, remote, scheduler, observable, veusz

with scheduler.create() as world:
    
    book_A = orderbook.Local(tickSize=0.01, label="A")
    book_B = orderbook.Local(tickSize=0.01, label="B")
    
    link = remote.TwoWayLink(remote.Link(), remote.Link())
    remote_A = orderbook.Remote(book_A, link)
    remote_B = orderbook.Remote(book_B, link)
    
    price_graph = veusz.Graph("Price")
    spread_graph = veusz.Graph("Bid-Ask Spread")
    cross_graph = veusz.Graph("Cross Bid-Ask Spread")
    
    arbitrager = trader.SAMM([remote_A, remote_B], strategy.Arbitrage())
     
    assetPrice = observable.Price(book_A)
    
    avg = observable.avg
    
    cross_AB = observable.CrossSpread(book_A, book_B)
    cross_BA = observable.CrossSpread(book_B, book_A)
    
    cross_graph += [cross_AB,
                    cross_BA,
                    avg(cross_AB),
                    avg(cross_BA)]
    
    spread_graph += [avg(observable.BidPrice(book_A)),
                     avg(observable.AskPrice(book_A)),
                     avg(observable.BidPrice(book_B)),
                     avg(observable.AskPrice(book_B))]
    
    
    price_graph += [assetPrice, 
                    avg(assetPrice, 0.15),
                    avg(assetPrice, 0.065),
                    avg(assetPrice, 0.015)]
    
    t_A = trader.SingleAsset(remote_A, strategy.LiquidityProvider())
    t_B = trader.SingleAsset(remote_B, strategy.LiquidityProvider())
    
    world.workTill(500)
    
    veusz.render("arbitrage", [price_graph, spread_graph, cross_graph])
"""