
def TwoSides(trader, orderFactoryT, eventGen, orderFunc):                
        """ Runs generic two side strategy 
        trader - single asset single market trader
        orderFactoryT - function to create orders: side -> *orderParams -> Order
        eventGen - event generator to be listened - we'll use its advise method to subscribe to
        orderFunc - function to calculate order parameters: Trader -> None | (side,*orderParams) 
        """        

        def wakeUp(signal):
            # determine side and parameters of an order to create
            res = orderFunc(trader)
            if res <> None:
                (side, params) = res
                # create order given side and parameters
                order = orderFactoryT(side)(*params)
                # send order to the order book
                trader.send(order)

        # start listening calls from eventGen
        eventGen.advise(wakeUp)
        return trader

def OneSide(trader, side, orderFactoryT, eventGen, orderFunc):                
    """ Initializes generic one side trader and makes it working
    orderBook - book to place orders in
    side - side of orders to create
    orderFactoryT - function to create orders: side -> *orderParams -> Order
    eventGen - event generator to be listened - we'll use its advise method to subscribe to
    orderFunc - function to calculate order parameters: Trader -> *orderParams 
    """        

    # we may calculate order factory right now
    orderFactory = orderFactoryT(side)

    def wakeUp(signal):
        # determine parameters of an order to create
        params = orderFunc(trader)
        # create an order with given parameters
        order = orderFactory(*params)
        # send the order to the order book
        trader.send(order)

    # start listening calls from eventGen
    eventGen.advise(wakeUp)

    return trader