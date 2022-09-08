from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, ForceResult, FullMatch, UnionMatch
from .kotobade_asobou import Kotoba
from utils.tools import COMMAND_HEADS

# 插件信息
__name__ = "言葉で遊ぼう"
__description__ = "/言葉: 言葉で遊ぼう"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/言葉 <単語>\n" \
            "使用例:\n" \
            "\t/言葉 せんせい"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

kotoba = Kotoba()

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("言葉"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch() >> "tango"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[twilight]))
async def group_message_listener(
    app: Ariadne,
    group: Group,
    member: Member,
    help: ForceResult[MessageChain],
    tango: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    answer = tango.result.display
    result = kotoba.enter_word(member.name, answer)
    await app.send_group_message(group, MessageChain(Plain(result)))
