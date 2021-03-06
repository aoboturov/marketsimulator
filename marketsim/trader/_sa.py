from marketsim import types, meta, getLabel, Side

from _base import Base

class SingleAsset(Base, types.ISingleAssetTrader):
    """ A trader that trades a single asset on a single market.
    
        Parameters:
        
        **orderBook**
            order book for the asset being traded
            
        **strategies**
            array of strategies run by the trader
            
        **amount** 
            current position of the trader (number of assets that it owns)
            
        **PnL**
            current trader balance (number of money units that it owns)
    """

    def __init__(self, orderBook, strategy, label=None, amount = 0, PnL=0, timeseries = []):
        Base.__init__(self, PnL, timeseries)
        self._orderBook = orderBook
        self._amount = amount
        self.strategy = strategy
        self._label = label
        self.label = self._label
        self._alias = [self._label]
             
    def reset(self):
        self._amount = 0
        
    _properties = {'amount'     : float, 
                   'strategy'   : types.ISingleAssetStrategy,
                   'orderBook'  : types.IOrderBook }
    
    _internals = ['_orderBook'] # hack in order to make it processed first
            
    
    @property
    def amount(self):
        """ Number of assets traded:
        positive if trader has bought more assets than sold them
        negative otherwise
        """
        return self._amount
    
    @amount.setter
    def amount(self, value):
        self._amount = value
        
    def _onOrderMatched_impl(self, order, other, (price, volume)):
        """ Called when a trader's 'order' is traded against 'other' order 
        at given 'price' and 'volume'
        Trader's amount and P&L is updated and listeners are notified about the trade   
        """
        self._amount += volume if order.side == Side.Buy else -volume
        Base._onOrderMatched_impl(self, order, other, (price, volume))
    
    @property
    def book(self): # obsolete
        return self._orderBook
    
    @property
    def orderBook(self):
        return self._orderBook
    
    @property
    def orderBooks(self):
        return [self._orderBook]
    
    @property
    def _digitsToShow(self):
        return self._orderBook._digitsToShow
    
    @orderBook.setter
    def orderBook(self, newvalue):
        self._orderBook = newvalue
        
    def send(self, order):
        Base.send(self, self._orderBook, order)
