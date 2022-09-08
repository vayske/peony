from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch, UnionMatch, ForceResult
from utils.tools import COMMAND_HEADS
import aiohttp

# 插件信息
__name__ = "彩虹屁"
__description__ = "/hi: 猫猫彩虹屁，用于测试bot是否在线"
__author__ = "SinceL"
__usage__ = "指令\n" \
            "\t/hi\n" \
            "使用例:\n" \
            "\t/hi"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("hi"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[twilight]))
async def group_message_listener(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    rainbow = await fetchRainbow()
    await app.send_group_message(group, MessageChain(Plain(rainbow)))

async def fetchRainbow():
    api = 'https://api.shadiao.app/chp'
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            json = await response.json()
            return json["data"]["text"]
