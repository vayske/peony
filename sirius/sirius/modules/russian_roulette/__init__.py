from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, FullMatch, ForceResult, UnionMatch

from random import shuffle
from utils.tools import COMMAND_HEADS

# 插件信息
__name__ = "Russian roulette"
__description__ = "/reload: 装填子弹\n" \
                  "/shoot: 开枪\n" \
                  "/spin: 转动弹巢"
__author__ = "EndEdge"
__usage__ = "指令:\n" \
            "\t/reload <子弹数>\n" \
            "\t/shoot <名字>\n" \
            "\t/spin\n" \
            "使用例:\n" \
            "\t/reload 5\n" \
            "\t/shoot tomcat\n" \
            "\t/spin"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)


class RussianRoulette:
    def __init__(self):
        self.bullet = 0
        self.magazine = []

    def reload(self, bullet) -> str:
        if bullet <= 0 or bullet > 5:
            return '子弹装填失败，有效子弹数为 1 ~ 5'
        self.bullet = bullet
        self.magazine = []
        for i in range(6):
            if bullet > 0:
                self.magazine.append(1)
                bullet -= 1
            else:
                self.magazine.append(0)
        shuffle(self.magazine)
        return '子弹装填成功'

    def shoot(self, name='你') -> str:
        if self.bullet == 0:
            return '子弹打完了，请重新装填'
        if self.magazine.pop(0) == 1:
            self.bullet -= 1
            return '你扣下了扳机，{}死了'.format(name)
        else:
            return '你扣下了扳机，但{}还活着'.format(name)

    def spin(self) -> str:
        if self.bullet == 0:
            return '子弹打完了，请重新装填'
        shuffle(self.magazine)
        return '转轮旋转成功'


russian_roulette = RussianRoulette()

reload: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("reload"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch(optional=True) >> "bullet"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[reload]))
async def reload_gun(
        app: Ariadne,
        group: Group,
        help: ForceResult[MessageChain],
        bullet: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    n_bullet = bullet.result.display if bullet.matched else '1'
    if not n_bullet.isdigit():
        await app.send_group_message(group, MessageChain(Plain('请输入数字')))
    else:
        await app.send_group_message(group, MessageChain(Plain(russian_roulette.reload(int(n_bullet)))))


shoot: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("shoot"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch(optional=True) >> "nickname"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[shoot]))
async def shoot_gun(
        app: Ariadne,
        group: Group,
        help: ForceResult[MessageChain],
        nickname: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    name = nickname.result.display if nickname.matched else '你'
    await app.send_group_message(group, MessageChain(Plain(russian_roulette.shoot(name))))


spin: Twilight = Twilight(
    [
        RegexMatch(COMMAND_HEADS),
        FullMatch("spin"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[spin]))
async def spin_gun(
        app: Ariadne,
        group: Group,
        help: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    await app.send_group_message(group, MessageChain(Plain(russian_roulette.spin())))
