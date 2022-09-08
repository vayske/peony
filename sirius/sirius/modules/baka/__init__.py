from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, UnionMatch, ForceResult, FullMatch
from utils.tools import COMMAND_HEADS

from random import choice


# 插件信息
__name__ = "猫猫骂他"
__description__ = "/baka: 猫猫骂他"
__author__ = "汤姆凯特"
__usage__ = "指令:\n" \
            "\t/baka <名字>\n" \
            "使用例:\n" \
            "\t/baka 凯特"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

bakaList = ['给\U0001F474爬', '小老弟行不行啊', '辣鸡']

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("baka"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch(optional=True) >> "message"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[twilight]))
async def baka(
    app: Ariadne,
    help: ForceResult[MessageChain],
    message: ForceResult[MessageChain],
    group: Group
):
    """
    Handle the "baka" command and send a message
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    baka = choice(bakaList)
    if message.matched:
        text: MessageChain =  message.result
        name = text.display
        await app.send_group_message(group, MessageChain(Plain(f'{name}{baka}')))
    else:
        await app.send_group_message(group, MessageChain(Plain(f'{baka}')))
