from marketsim import bind, meta, context

class Event(object):
    """ Multicast event
    
    Keeps a set of callable listeners 
    """

    def __init__(self):
        self._listeners = set()
        self.fire = bind.Method(self, '_fire_impl')
        
#    _internals = ['_listeners']
        
    def __iadd__(self, listener):
        """ Adds 'listener' to the listeners set
        """
        self._listeners.add(listener)
        return self
    
    def __isub__(self, listener):
        self._listeners.remove(listener)
        return self
        
    def _fire_impl(self, *args):
        """ Calls all listeners passing *args to them
        """
        for x in list(self._listeners):
            x(*args)
            
from blist import sorteddict

class Conditional(Event):
    
    def __init__(self, getter):
        Event.__init__(self)
        self._getter = getter
        self._less = sorteddict()
    
    def __iadd__(self, listener):
        if '_lessThan' in dir(listener):
            bound = listener._lessThan()
            if bound not in self._less:
                self._less[bound] = []
            self._less[bound].append(listener)
        else:
            Event.__iadd__(self, listener)
            
    def __isub__(self, listener):
        if '_lessThan' in dir(listener):
            bound = listener._lessThan()
            self._less[bound].remove(listener)
        else:
            Event.__isub__(self, listener)
            
    def _fire_impl(self, *args):
        bound = self._getter(*args)
        for listener in self._less:
            if listener._lessThan() < bound:
                listener(*args)
        Event._fire_impl(self, *args)
                
            

class Array(Event):
    
    def __init__(self, events):
        self._events = []
        self.events = events
        
    _properties = { 'events' : meta.listOf(Event) }
        
    @property
    def events(self):
        return self._events
    
    @events.setter
    def events(self, value):
        for ev in self._events:
            ev -= self.fire
        self._events = value
        for ev in self._events:
            ev += self.fire
            
    def dispose(self):
        for ev in self._events:
            ev -= self.fire
        
        
        
    
            
class Subscription(object):
    
    def __init__(self, event, listener):
        self._event = event 
        self._listener = listener
        self._subscribed = False # in fact it is _bound but its cleaning is not yet supported at dispose
        
    _internals = ['_event']
    
    @property
    def event(self):
        return self._event
    
    @event.setter
    def event(self, value):
        self._event -= self._listener
        self._event = value
        self._event += self._listener
        
    def switchTo(self, newEvent):
        self._event -= self._listener
        self._event = newEvent
        self._event += self._listener
        
    def bind(self, context):
        self._event += self._listener
        self._subscribed = True
        
    def dispose(self):
        if self._subscribed:
            self._event -= self._listener
            self._subscribed = False
                
def dispose(obj):
    if '_subscriptions' in dir(obj):
        for x in obj._subscriptions:
            x.dispose()
    if '_children_to_visit' in dir(obj):
        for child in obj._children_to_visit:
            if 'dispose' in dir(child):
                child.dispose()
            
                
def subscribe(event, listener, target = None, ctx = None):
    
    subscription = Subscription(event, listener)
    
    if target is not None:
        if '_subscriptions' not in dir(target):
            target._subscriptions = []
            
        target._subscriptions.append(subscription)
        
        if 'dispose' not in dir(target):
            target.dispose = bind.Callable(dispose, target)
            
    if ctx is not None:
        context.bind(subscription, ctx)
            
    return subscription
            
        
