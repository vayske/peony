from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, FullMatch, ForceResult, UnionMatch
from utils.tools import COMMAND_HEADS

# 插件信息
__name__ = "Speak"
__description__ = "/speak: 复读消息"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/speak <消息>\n" \
            "使用例:\n" \
            "\t/speak 给我们一个信号"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

say: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("speak"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "message"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[say]))
async def group_message_listener(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    message: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    msg = message.result.content
    for i in range(len(msg)):
        if isinstance(msg[i], Image):
            msg[i].id = None
    await app.send_group_message(group, MessageChain(msg))
