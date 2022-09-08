from graia.broadcast.entities.event import BaseEvent
from graia.ariadne.dispatcher import ContextDispatcher, MessageChainDispatcher, SourceDispatcher
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface


class BilibiliLiveReminder(BaseEvent):
    """
    The live reminder event class
    """
    class Dispatcher(BaseDispatcher):
        mixin = [ContextDispatcher, MessageChainDispatcher, SourceDispatcher]

        @staticmethod
        async def catch(interface: DispatcherInterface):
            pass

class BilibiliVideoReminder(BaseEvent):
    """
    The video reminder event class
    """
    class Dispatcher(BaseDispatcher):
        mixin = [ContextDispatcher, MessageChainDispatcher, SourceDispatcher]

        @staticmethod
        async def catch(interface: DispatcherInterface):
            pass
