from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, ForceResult, FullMatch, UnionMatch
from graia.broadcast.builtin.decorators import Depend
import sys, os, subprocess

from utils.tools import COMMAND_HEADS, require_member

# 插件信息
__name__ = "Github"
__description__ = "/checkout: 更新/切换Branch,可用于重启bot"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/checkout <branch>\n" \
            "使用例:\n" \
            "\t/checkout master"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

GROUP = {
    1: 2,
    2: 3,
    3: 4,
}

twilight: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("checkout"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch() >> "branch"
    ]
)
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[twilight],
        decorators=[Depend(require_member(123456))]
    )
)
async def checkout(
    app: Ariadne,
    help: ForceResult[MessageChain],
    branch: ForceResult[MessageChain],
    group: Group
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    branch_name = branch.result.display
    path = os.getcwd()
    result = subprocess.run(['sh', f'{path}/modules/github/scripts/checkout_branch.sh', branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        await app.send_group_message(group, MessageChain(Plain(result.stderr)))
    else:
        await app.send_group_message(group, MessageChain(Plain(result.stdout)))
        exit(GROUP[group.id])


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def group_message_listener(
    app: Ariadne
):
    msg = ""
    if len(sys.argv) == 3:
        code = int(sys.argv[1])
        msg = sys.argv[2]
        for gid in GROUP:
            if GROUP[gid] == code:
                group = gid
        await app.send_group_message(group, MessageChain(Plain(f'重启完毕，当前Branch：{msg}')))
