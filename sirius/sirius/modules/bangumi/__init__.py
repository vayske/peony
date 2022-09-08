import asyncio
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch, UnionMatch, ForceResult
from utils.tools import COMMAND_HEADS
from .event import BangumiTime
from datetime import datetime, timedelta
import aiohttp

# 插件信息
__name__ = "新番列表"
__description__ = "/bangumi: 获取当日新番列表"
__author__ = "SinceL"
__usage__ = "指令\n" \
            "\t/bangumi\n" \
            "使用例:\n" \
            "\t/bangumi"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("bangumi"),
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
    bangumi_list = await fetch_bangumi()
    msg = [Plain('##今日新番##\n')]
    for bangumi in bangumi_list:
        msg.append(Plain(f"{bangumi}\n"))
    await app.send_group_message(group, MessageChain(msg))

async def fetch_bangumi():
    list_api = 'https://bangumi.moe/api/bangumi/current'
    dt = datetime.now() + timedelta(hours=16)
    day = int(dt.strftime('%w')) - 1
    if day < 0:
        day = 6
    async with aiohttp.ClientSession() as session:
        async with session.get(list_api) as response:
            bangumi_list = await response.json()
        bangumi_today = [ v['name'] for v in bangumi_list if v['showOn'] == day ]
    return bangumi_today


async def check_bangumi():
    update = False
    remind_time = 18
    await asyncio.sleep(5)
    while True:
        time = datetime.now() + timedelta(hours=16)
        if not update and time.hour == remind_time:
            bcc.postEvent(BangumiTime())
            update = True
        elif update and time.hour != remind_time:
            update = False
        await asyncio.sleep(360)

@channel.use(ListenerSchema(listening_events=[BangumiTime]))
async def post_bangumi(app: Ariadne):
    groups = await app.get_group_list()
    for group in groups:
        bangumi_list = await fetch_bangumi()
        msg = [Plain('##昨日新番##\n')]
        for bangumi in bangumi_list:
            msg.append(Plain(f"{bangumi}\n"))
        await app.send_group_message(group, MessageChain(msg))

reminder = bcc.loop.create_task(check_bangumi())
