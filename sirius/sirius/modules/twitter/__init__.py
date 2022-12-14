import aiohttp
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, SpacePolicy

from loguru import logger
import os


# 插件信息
__name__ = "TwitterPreview"
__description__ = "推特链接预览"
__author__ = "SinceL"
__usage__ = "自动使用"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法: {__usage__}")
channel.author(__author__)

bearer_token = os.environ.get("BEARER_TOKEN")
header = {'Authorization': f'Bearer {bearer_token}', 'User-Agent': 'v2TweetLookupPython'}

def generateApi(url: str):
    token = url.split('status/')[-1]
    tid = token.split('?')[0]
    return f'https://api.twitter.com/2/tweets?ids={tid}&tweet.fields=possibly_sensitive&expansions=attachments.media_keys,author_id&media.fields=url,preview_image_url&user.fields=name'


check_link: Twilight = Twilight(
    [
        RegexMatch(r'https://twitter.com/.*')
    ]
)
@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[check_link]))
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    url = message.display
    msg = []
    logger.info(f'Receive Twitter URL: {url}')
    api = generateApi(url)
    session = aiohttp.ClientSession()
    async with session.get(api, headers=header) as response:
        data = await response.json()
        if 'data' in data:
            restrict = data['data'][0]['possibly_sensitive']
            if restrict:
                logger.info(f'Skip sensitive content')
                await session.close()
                return
            text = data['data'][0]['text']
            account = data['includes']['users'][0]['username']
            name = data['includes']['users'][0]['name']
            msg.append(Plain(f'{name} {account}:\n{text}'))
            if 'media' in data['includes']:
                for media in data['includes']['media']:
                    if media['type'] == 'photo':
                        msg.append(Image(url=media['url']))
                    else:
                        msg.append(Image(url=media['preview_image_url']))
    await session.close()
    if len(msg) > 0:
        await app.send_group_message(group, MessageChain(msg))
