from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, FullMatch, ForceResult
from utils.tools import COMMAND_HEADS


# 插件信息
__name__ = "Help"
__description__ = "/help: Bot指令菜单"
__author__ = "SinceL"
__usage__ = "发送/help"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

help: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("help")
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[help]))
async def group_message_listener(
    app: Ariadne,
    group: Group,
):
    command_list = []
    for ch in saya.channels:
        if saya.channels[ch]._description.startswith("/"):
            command_list.append(f"{saya.channels[ch]._description}")
    command_list.sort()
    msg = MessageChain(f"##Bot指令菜单##\n可用指令头: {COMMAND_HEADS}\n")
    for command in command_list:
        msg = msg + MessageChain(f"{command}\n")
    msg = msg + MessageChain("使用<指令> <-h|--help>查看详情")
    await app.send_group_message(group, msg)
