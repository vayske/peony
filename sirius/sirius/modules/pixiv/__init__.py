import asyncio
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image, Forward, ForwardNode
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, UnionMatch, ParamMatch, FullMatch, ForceResult
from .pixiv_api import Pixiv
from .event import SetuTime
from utils.tools import COMMAND_HEADS
from datetime import datetime
from loguru import logger
import os

# 插件信息
__name__ = "/hso"
__description__ = "/hso: P站Api"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/hso [-x|-r|-r18] <tag|id>\n" \
            "使用例:\n" \
            "\t/hso リコリコ\n" \
            "\t/hso 100285476"

pixiv = Pixiv()

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

loop = asyncio.get_event_loop()

bcc = saya.broadcast

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("hso"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        UnionMatch("-x", "-r", "-r18", optional=True) >> "r18",
        ParamMatch(optional=True) >>  "tag"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[twilight]))
async def get_image(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    r18: ForceResult[MessageChain],
    tag: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    result = None
    if not tag.matched:
        result = await pixiv.daily_rank(r18.matched)
    else:
        token = tag.result.display
        if token.isdigit():
            result = await pixiv.fetch_image(token, r18.matched)
        else:
            result = await pixiv.tag_search(token, r18.matched)

    if result is None:
        await app.send_group_message(group, MessageChain(Plain('没有搜到相关图片')))
    else:
        title, address, link, r18 = result
        member = await app.get_member(group, app.account)
        fwd_nodeList = [
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain(Image(path=address)),
            ),
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain(Plain(f'{title} {link}')),
            )
        ]
        await app.send_group_message(group, MessageChain(Forward(nodeList=fwd_nodeList)))

# Image Preview
check_link: Twilight = Twilight(
    [
        RegexMatch(r'https://www.pixiv.net/artworks/.*')
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[check_link]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    url = message.display
    logger.info(f'Receive Pixiv URL: {url}')
    id = url.split('artworks/')[-1]
    if id.isdigit():
        title, address, link, r18 = await pixiv.fetch_image(id)
        member = await app.get_member(group, app.account)
        fwd_nodeList = [
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain(Image(path=address)),
            ),
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain(Plain(f'{title} {link}')),
            )
        ]
        await app.send_group_message(group, MessageChain(Forward(nodeList=fwd_nodeList)))


async def daily_setu():
    while True:
        await asyncio.sleep(60*60*25)
        bcc.postEvent(SetuTime())

@channel.use(ListenerSchema(listening_events=[SetuTime]))
async def setu(app: Ariadne):
    groups = await app.get_group_list()
    for group in groups:
        title, address, link, r18 = await pixiv.daily_rank(False)
        message = MessageChain(Image(path=address), Plain(f'{title}{link}'))
        await app.send_group_message(group, message)

reminder = bcc.loop.create_task(daily_setu())
