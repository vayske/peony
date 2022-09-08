import asyncio
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, ForceResult, FullMatch, UnionMatch
from loguru import logger
from utils.tools import COMMAND_HEADS, create_json
from .bilibili_api import Bilibili
from .event import BilibiliLiveReminder, BilibiliVideoReminder
from os import getcwd

# 插件信息
__name__ = "Bilibili"
__description__ = "/follow: 关注一个或多个up主\n" \
                  "/unfollow: 取消关注一个或多个up主\n" \
                  "/list: 列出已关注的up主"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/follow <bid1> <bid2> ...\n" \
            "\t/unfollow <bid1> <bid2> ...\n" \
            "\t/list\n" \
            "使用例:\n" \
            "\t/follow 488978908\n" \
            "\t/unfollow 488978908\n" \
            "\t/list"

up_list = getcwd() + '/modules/bilibili/follows.json'
create_json(up_list)
bilibili = Bilibili(up_list)

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

follow: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("follow"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "ids"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[follow]))
async def follow_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    ids: ForceResult[MessageChain]
) -> None:
    """
    Handle the "follow" command and send a message related to the status
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    bids = ids.result.display.split()
    names = await bilibili.follow(group.id, bids)
    length = len(names)
    if length == 0:
        await app.send_group_message(group, MessageChain(Plain('关注失败')))
    else:
        message = []
        for i in range(length):
            if i == (length - 1):
                message.append(Plain(f'关注 {names[i]} 成功'))
            else:
                message.append(Plain(f'关注 {names[i]} 成功\n'))
        await app.send_group_message(group, MessageChain(message))


unfollow: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("unfollow"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "ids"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[unfollow]))
async def unfollow_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    ids: ForceResult[MessageChain]
) -> None:
    """
    Handle the "unfollow" command and send a message
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    bids = ids.result.display.split()
    names = await bilibili.unfollow(group.id, bids)
    length = len(names)
    if length == 0:
        await app.send_group_message(group, MessageChain(Plain('取消关注失败')))
    else:
        message = []
        for i in range(length):
            if i == (length - 1):
                message.append(Plain(f'取消关注 {names[i]} 成功'))
            else:
                message.append(Plain(f'取消关注 {names[i]} 成功\n'))
        await app.send_group_message(group, MessageChain(message))


show_list: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("list"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[show_list]))
async def list_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
) -> None:
    """
    Handle the "list" command and send a message
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    mylist = await bilibili.list_users(group.id)
    message = []
    link = 0
    for name in mylist:
        message.append(Plain(name))
        link += 1
        if link == 5:
            await app.send_group_message(group, MessageChain(message))
            message.clear()
            link = 0
    if len(message) != 0:
        await app.send_group_message(group, MessageChain(message))
    return


check_live: Twilight = Twilight(
    [
        RegexMatch(r'https://live.bilibili.com/.*')
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[check_live]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    url = message.display
    logger.info(f'Receive Bilibili Live URL: {url}')
    rid = url.split('https://live.bilibili.com/')[-1].split('?')[0]
    if rid.isdigit():
        (cover, title, link) = await bilibili.get_live_by_roomid(rid)
        await app.send_group_message(group, MessageChain(Image(url=cover), Plain(f"{title} {link}")))


@channel.use(ListenerSchema(listening_events=[BilibiliLiveReminder]))
async def remind_lives(app: Ariadne) -> None:
    """
    Check for live status and send a message
    """
    lives = await bilibili.check_lives()
    for uid in lives:
        cover = lives[uid]['cover']
        title = lives[uid]['title']
        up = lives[uid]['up']
        link = lives[uid]['link']
        message = MessageChain(Image(url=cover), Plain(f'{title} Up: {up} 正在直播{link}')) # type: ignore
        for group in lives[uid]['groups']:
            await app.send_group_message(group, message) # type: ignore

@channel.use(ListenerSchema(listening_events=[BilibiliVideoReminder]))
async def remind_videos(app: Ariadne) -> None:
    """
    Check for live status and send a message
    """
    videos = await bilibili.check_videos()
    for bv in videos:
        cover = videos[bv]['cover']
        title = videos[bv]['title']
        up = videos[bv]['up']
        link = videos[bv]['link']
        message = MessageChain(Image(url=cover), Plain(f"{title} Up: {up} {link}")) # type: ignore
        for group in videos[bv]['groups']:
            await app.send_group_message(group, message) # type: ignore

async def _check_update() -> None:
    """
    A task that checks for user status every 10 mins
    """
    await asyncio.sleep(5)
    while True:
        bcc.postEvent(BilibiliVideoReminder())
        bcc.postEvent(BilibiliLiveReminder())
        await asyncio.sleep(600)


bcc.loop.create_task(_check_update())
