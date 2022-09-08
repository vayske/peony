from loguru import logger
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Quote
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, FullMatch, ForceResult
from graia.broadcast.builtin.decorators import Depend

from utils.tools import COMMAND_HEADS, require_member
from .repeat_api import Repeat

# 插件信息
__name__ = "复读姬"
__description__ = "随机复读接收到的非指令消息，或有三次以上消息重复时+1"
__author__ = "SinceL"
__usage__ = "发送消息触发"

repeat = Repeat(1)
saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法: {__usage__}")
channel.author(__author__)

set_repeat: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("repeat"),
        ParamMatch() >> "rate",
    ]
)
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[set_repeat],
        decorators=[Depend(require_member(123456))]
    )
)
async def set_rate(
    rate: ForceResult[MessageChain],
):
    new_rate = rate.result.display
    logger.info(f'Setting repeat rate to {rate}')
    repeat.set_rate(new_rate)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    sender: Member,
    group: Group
):
    text = message.display
    if text[0] not in "/$#!%-":
        message_sendable = message.as_sendable()
        if repeat.is_repeat(group, sender, message_sendable):
            for i in range(len(message_sendable)):
                if isinstance(message_sendable[i], Image): # type: ignore
                    message_sendable[i].id = None # type: ignore
            quote_id = message.get(Quote)[0].id if message.has(Quote) else None
            await app.send_group_message(group, message_sendable, quote=quote_id)
