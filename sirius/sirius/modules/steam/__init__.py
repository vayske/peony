from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, UnionMatch, ParamMatch, FullMatch, ForceResult
from graia.ariadne.message.element import Plain, Image
from .steam_api import SteamApi
from utils.tools import COMMAND_HEADS, create_json
import os

# 插件信息
__name__ = "Steam"
__description__ = "/steam: Steam好友api"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/steam [add <nickname> <id>|remove <nickname>|<nickname>|all]\n" \
            "使用例:\n" \
            "\t/steam add tomcat 123456789\n" \
            "\t/steam remove tomcat\n" \
            "\t/steam tomcat\n" \
            "\t/steam all"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

config = os.getcwd() + '/modules/steam/users.json'
create_json(config)
api_key = os.environ.get("STEAM_KEY")
steam = SteamApi(key=api_key, config_path=config)

command = "steam"

# Add or Remove user
actions: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        UnionMatch("add", "remove") >> "option",
        ParamMatch() >>  "nickname",
        ParamMatch(optional=True) >>  "id"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[actions]))
async def add_user(
    app: Ariadne,
    group: Group,
    option: ForceResult[MessageChain],
    nickname: ForceResult[MessageChain],
    id: ForceResult[MessageChain]
):
    action = option.result.display
    name = nickname.result.display
    if action == "add" and id.matched:
        sid = id.result.display
        result = await steam.add_user(name, sid)
    elif action == "remove":
        result = await steam.remove_user(name)
    await app.send_group_message(group, MessageChain(Plain(result)))


# Get status of user(s)
get_status: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        ParamMatch() >>  "nickname",
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[get_status]))
async def get_user(
    app: Ariadne,
    group: Group,
    nickname: ForceResult[MessageChain],
):
    name = nickname.result.display
    status_list = []
    if name == "all":
        status_list = await steam.list_all()
    else:
        status = await steam.get_status(name)
        status_list.append(status)
    num_users = len(status_list)
    message = []
    for i in range(num_users):
        avatar, display_name, status = status_list[i] # type: ignore
        if display_name:
            if i == (num_users - 1):
                message.append(Image(url=avatar))
                message.append(Plain(f"{display_name}{status}"))
            else:
                message.append(Image(url=avatar))
                message.append(Plain(f"{display_name}{status}\n"))
    if len(message) > 0:
        await app.send_group_message(group, MessageChain(message))


# Help message
help: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch(command),
        UnionMatch("-h", "--help", optional=True) >> "help"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[help]))
async def get_help(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
