from marketsim.veusz_graph import Graph, showGraphs
from marketsim.scheduler import Scheduler, Timer
from marketsim.order_queue import OrderBook
from marketsim import Side
from marketsim.indicator import AssetPrice, BidPrice, AskPrice, OnEveryDt, EWMA, TraderEfficiency, PnL
from random import random, expovariate

from marketsim import strategy, trader

world = Scheduler()

def avg(source, alpha=0.15):
    return OnEveryDt(1, EWMA(source, alpha))

book_A = OrderBook(tickSize=0.01, label="A")

price_graph = Graph("Price")
 
assetPrice = AssetPrice(book_A)

price_graph.addTimeSeries([\
    assetPrice,
    avg(assetPrice, alpha=0.15),
    avg(assetPrice, alpha=0.015),
    avg(assetPrice, alpha=0.65)])

def volume(v):
    return lambda: v*expovariate(.1)

lp_A = strategy.LiquidityProvider(trader.SASM_Trader(book_A, "A"), volumeDistr=volume(10))
lp_a = strategy.LiquidityProvider(trader.SASM_Trader(book_A, "a"), volumeDistr=volume(1))

spread_graph = Graph("Bid-Ask Spread")

spread_graph.addTimeSerie(BidPrice(book_A))
spread_graph.addTimeSerie(AskPrice(book_A))

lp_a.efficiency = TraderEfficiency([lp_a.on_traded], lp_a)

eff_graph = Graph("efficiency")
eff_graph.addTimeSerie(lp_a.efficiency)
eff_graph.addTimeSerie(PnL(lp_a))

world.workTill(500)

showGraphs("liquidity", [price_graph, spread_graph, eff_graph])
