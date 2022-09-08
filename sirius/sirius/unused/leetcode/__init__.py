from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from .leetcode_time import LeetCodeTime
from .leetcode_api import LeetCode
import os
import asyncio
from datetime import datetime


# 插件信息
__name__ = "Leetcode"
__description__ = ""
__author__ = ""
__usage__ = ""

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法: {__usage__}")
channel.author(__author__)

bcc = saya.broadcast
lc_username = os.environ.get("LC_USR")
lc_password = os.environ.get("LC_PW")
lc = LeetCode(lc_username, lc_password)


@channel.use(ListenerSchema(listening_events=[LeetCodeTime]))
async def post_question(app: Ariadne):
    groups = await app.get_group_list()
    image, url = await lc.get_question()
    if image is not None:
        for group in groups:
            message = MessageChain(Image(path=image), Plain(f'{url}'))
            await app.send_group_message(group, message)
            await asyncio.sleep(15)
        lc.clean()

async def daily_leetcode():
    while True:
        time = datetime.now().strftime("%H")
        if time == "18":
            bcc.postEvent(LeetCodeTime())
        await asyncio.sleep(60*60)


bcc.loop.create_task(daily_leetcode())
