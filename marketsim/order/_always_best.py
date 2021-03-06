from marketsim import Side, registry, meta, types, bind, event
from _base import Base
from _limit import LimitFactory
from _cancel import Cancel
from marketsim.types import *

class AlwaysBest(Base):
    
    def __init__(self, side, orderFactoryT, volume):
        
        Base.__init__(self, side, volume)

        self._factory = orderFactoryT(side)
        self._current = None
        
    def _onOrderMatched(self, my, other, pv):
        self.onMatchedWith(other, pv)
        if self._volume == 0:
            self._subscription.dispose()
            del self._subscription 
    
    def _onBestOrderChanged(self, queue):
        if not queue.empty and queue.best != self._current:
            if self._current is not None:
                self._orderSubscription.dispose()
                queue.book.process(Cancel(self._current))
            if not self.empty and not self.cancelled:
                price = queue.best.price
                tick = queue.book.tickSize
                price += tick if self.side == Side.Buy else -tick
                self._current = self._factory(price, self.volume)
                self._orderSubscription = \
                    event.subscribe(self._current.on_matched, 
                                    bind.Method(self, '_onOrderMatched'),
                                    self)
                self._orderSubscription.bind(None)
                queue.book.process(self._current)
        
    def processIn(self, book):
        self._onBestOrderChanged(book.queue(self.side))
        self._subscription = event.subscribe(
                                book.queue(self.side).on_best_changed,
                                bind.Method(self, '_onBestOrderChanged'),
                                self)
        self._subscription.bind(None)

@registry.expose(['AlwaysBest'])
class AlwaysBestFactory(object):
    """ AlwaysBest is a virtual order that ensures that it has the best price in the order book. 
    It is implemented as a limit order which is cancelled 
    once the best price in the order queue has changed 
    and is sent again to the order book 
    with a price one tick better than the best price in the book.
    """
    
    def __init__(self, orderFactory = LimitFactory):
        self.orderFactory = orderFactory
        
    _types = [meta.function(args=(Side,), rv=function((Volume,), IOrder))]
        
    _properties = {'orderFactory' : meta.function((types.Side,), meta.function((types.Price, types.Volume), types.IOrder))}
    
    def __call__(self, side):
        return bind.Construct(AlwaysBest, side, self.orderFactory)
        