from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, UnionMatch, ForceResult
from utils.tools import COMMAND_HEADS
import aiohttp

# 插件信息
__name__ = "random cat"
__description__ = "/cat: 随机猫图"
__author__ = "神•凯特"
__usage__ = "指令:\n" \
            "\t/cat\n" \
            "使用例:\n" \
            "\t/cat"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        RegexMatch(r"(cat)+"),
        UnionMatch("-h", "--help", optional=True) >> "help",
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[twilight]))
async def group_message_listener(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
):
    """
    Handle the "cat" command and send a message
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": "e3754236-5e47-47cc-bd58-dd0a8061fb89"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            responseData = await response.json()
            imgURL = responseData[0]["url"]
            await app.send_group_message(group, MessageChain(Image(url=imgURL)))
