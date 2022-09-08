from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, RegexMatch, ParamMatch, ForceResult, UnionMatch
from utils.tools import COMMAND_HEADS
from .OXgame import OXgameCore
from typing import Dict

# 插件信息
__name__ = "Game"
__description__ = "/ox: 井字棋"
__author__ = "汤姆凯特"
__usage__ = "指令:\n" \
            "\t/ox [join|move <x> <y>]\n" \
            "使用例:\n" \
            "\t/ox join\n" \
            "\t/ox move 0 0"

ox_game: Dict[int, OXgameCore] = {}

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

command = 'ox'

help: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        UnionMatch("-h", "--help", "help", optional=True) >> "help",
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[help]))
async def get_help(
    app: Ariadne,
    group: Group,
):
    await app.send_group_message(group, MessageChain(Plain(__usage__)))

join_game: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        FullMatch("join"),
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[join_game]))
async def user_join(
    app: Ariadne,
    sender: Member,
    group: Group,
):
    if group.id not in ox_game:
        ox_game[group.id] = OXgameCore()
    status = ox_game[group.id].add_player(sender.name)
    await app.send_group_message(group, MessageChain(Plain(status)))

move: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        FullMatch("move"),
        ParamMatch() >> "x",
        ParamMatch() >> "y",
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[move]))
async def user_move(
    app: Ariadne,
    sender: Member,
    group: Group,
    x: ForceResult[MessageChain],
    y: ForceResult[MessageChain],
):
    move_x = x.result.display
    move_y = y.result.display
    player = sender.name
    result = ox_game[group.id].move(player, int(move_x), int(move_y))
    await app.send_group_message(group, MessageChain(Plain(result)))
