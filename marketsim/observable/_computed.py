from marketsim import Event, getLabel, Side, scheduler, types, meta, mathutils

class IndicatorBase(types.IObservable):
    """ Indicator that stores some scalar value and knows how to update it
    """
    def __init__(self, eventSources, dataSource, label, attributes = {}):
        """ Initializes indicator
        eventSources -- sequence of events to be subscribed to 
        dataSource -- function to be called in order to obtain the value
        label -- indicator label to be shown, for example, on a graph
        attributes -- a dictionary of attributes to be associated with the indicator
        """
        
        
        self.label = label
        self.attributes = attributes
        self._eventSources = []
        self.eventSources = eventSources
        self._dataSource = dataSource
        self.on_changed = Event()
            
        self.update(None)
        
    _properties = { 'dataSource'   : meta.function((), float),
                    'eventSources' : meta.listOf(Event),
                    'label'        : str  }
    
    # this event is called when currentValue updates        
    def update(self, _):
        # calculate current value
        self._current = self._dataSource()
        if self._current is not None: # this should be removed into a separate filter
            self.on_changed.fire(self) 
    
    @property
    def eventSources(self):
        return self._eventSources
    
    @eventSources.setter
    def eventSources(self, value):
        for es in self._eventSources:
            es.unadvise(self.update)
        self._eventSources = value
        for es in self._eventSources:
            es.advise(self.update)
    
    @property
    def dataSource(self):
        return self._dataSource
    
    @dataSource.setter
    def dataSource(self, value):
        self._dataSource = value
    
    @property
    def _alias(self):
        return self.label
    
    @_alias.setter
    def _alias(self, value):
        self.label = value
        
    def reset(self):
        self._current = None
        if 'reset' in dir(self._dataSource):
            self._dataSource.reset()
        for es in self._eventSources:
            es.reset()
            
    def schedule(self):
        self.reset()
                
    def advise(self, listener):
        """ Subscribes 'listener' to value change event
        """
        self.on_changed += listener
        
    def unadvise(self, listener):
        self.on_changed -= listener
        
    @property
    def value(self):
        """ Returns current value
        """
        return self._current

class rough_balance(object):
    
    def __init__(self, trader):
        self.trader = trader
        
    _types = [meta.function((), float)]
    
    def __call__(self):
        return self.trader.PnL + self.trader.amount*self.trader.book.price if self.trader.book.price else 0
    
    _properties = { 'trader' : types.ISingleAssetTrader }


class OnTraded(Event):
    """ Multicast event
    
    Keeps a set of callable listeners 
    """

    def __init__(self, trader):
        Event.__init__(self)
        self.trader = trader
        self.trader.on_traded += self.fire
        
    _properties = { 'trader' : types.ISingleAssetTrader }
    
    
def InstEfficiency(trader):
    
    return IndicatorBase([OnTraded(trader)], 
                         rough_balance(trader),
                         "InstEfficiency_{" + getLabel(trader) + "}")

class profit_and_loss(object):
    
    def __init__(self, trader):
        self.trader = trader
        
    _types = [meta.function((), float)]
    
    def __call__(self):
        return self.trader.PnL
    
    _properties = { 'trader' : types.ISingleAssetTrader }
    
def PnL(trader):
    
    return IndicatorBase([OnTraded(trader)], profit_and_loss(trader), "P&L_{"+getLabel(trader)+"}")

class mid_price(object):
    
    def __init__(self, orderbook):
        self.orderbook = orderbook
        
    _types = [meta.function((), float)]
    
    def __call__(self):
        return self.orderbook.price
    
    _properties = { 'orderbook' : types.IOrderBook }
    
class OnPriceChanged(Event):
    
    def __init__(self, orderbook):
        Event.__init__(self)
        self.orderbook = orderbook
        self.orderbook.on_price_changed += self.fire
        
    _properties = { 'orderbook' : types.IOrderBook }
    
def Price(book):
    """ Creates an indicator bound to the middle price of an asset
    """   
    return IndicatorBase(\
        [OnPriceChanged(book)], 
        mid_price(book), "Price_{"+getLabel(book)+"}")
    
class OnSideBestChanged(Event):
    
    def __init__(self, orderbook, side):
        Event.__init__(self)
        self.orderbook = orderbook
        self.side = side
        self.orderbook.queue(self.side).on_best_changed += self.fire
        
    _properties = { 'orderbook' : types.IOrderBook, 
                    'side'      : types.Side }
    
def CrossSpread(book_A, book_B):
    asks = book_A.asks
    bids = book_B.bids
    return IndicatorBase(\
        [asks.on_best_changed, bids.on_best_changed], 
        lambda: asks.best.price - bids.best.price if not asks.empty and not bids.empty else None, 
        "Price("+asks.label+") - Price("+bids.label+")")

class volume_traded(object):
    
    def __init__(self, trader):
        self.trader = trader
        
    _types = [meta.function((), float)]
    
    def __call__(self):
        return self.trader.amount
    
    _properties = { 'trader' : types.ISingleAssetTrader }

    
def VolumeTraded(trader):
    return IndicatorBase(\
        [OnTraded(trader)], 
        volume_traded(trader), 
        "Amount_{"+getLabel(trader)+"}")
    
class side_price(object):
    
    def __init__(self, orderbook, side):
        self.orderbook = orderbook
        self.side = side
        
    _types = [meta.function((), float)]
    
    def __call__(self):
        queue = self.orderbook.queue(self.side)
        return queue.best.price if not queue.empty else None
    
    _properties = { 'orderbook' : types.IOrderBook, 
                    'side'      : types.Side }
    

def BestPrice(book, side, label):
    """ Creates an indicator bound to the price of the best order in a queue
    book - asset order book
    side - side of the queue
    label - label prefix
    """
    
    queue = book.queue(side)

    return IndicatorBase(\
        [OnSideBestChanged(book, side)], 
        side_price(book, side),
        "Price("+queue.label+")")
    
def BidPrice(book):
    """ Creates an indicator bound to the bid price of the asset
    book - asset order book
    """
    return BestPrice(book, Side.Buy, "BidPrice ")

def AskPrice(book):
    """ Creates an indicator bound to the ask price of the asset
    book - asset order book
    """
    return BestPrice(book, Side.Sell, "AskPrice ")

def OnEveryDt(interval, source):
    """ Creates an indicator that is updated regularly
    interval - constant interval between updates
    source - function to obtain indicator value
    """
    
    return IndicatorBase([scheduler.Timer(mathutils.constant(interval))],
                         source, 
                         getLabel(source), 
                         {'smooth':True})
