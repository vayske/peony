from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from bs4 import BeautifulSoup
from graia.ariadne.message.element import Plain, Image, Quote
from typing import Dict, Union
import requests

# 插件信息
__name__ = "FindSource"
__description__ = "/source: 查询图片出处"
__author__ = "EndEdge"
__usage__ = "指令:\n" \
            "\t/source\n" \
            "使用例:\n" \
            "\t回复带有图片的消息\"/source\""

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

url = "https://saucenao.com/search.php"

message_cache: Dict[int, MessageChain] = {}


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
        app: Ariadne,
        message: MessageChain,
        group: Group
):
    text = message.display
    if '/source' in text:
        if Quote in message:
            quote = message.get(Quote)[0]
            # fetch the original message that the reply refers to. The given api quote.origin can fetch the original
            # messageChain, but the Image inside is transcoded to Plain text (we can't get the original image this way).
            original_event = await app.get_message_from_id(messageId=quote.id)
            if not original_event:
                return
            last_message = original_event.message_chain
        else:
            last_message = message_cache[group.id] if group.id in message_cache else None # type: ignore
        if not last_message or Image not in last_message:
            return
        image = last_message.get(Image)[0]
        image_bytes = await image.get_bytes()
        try:
            msg = await find_source(image_bytes)
            await app.send_group_message(group, MessageChain(msg))
        except Exception as e:
            print(e)
    message_cache[group.id] = message
    return


async def find_source(img):
    files = (
        ('file', ("image", img, "image/jpg")),
        ('dbs[]', (None, '5')),
        ('dbs[]', (None, '8')),
        ('dbs[]', (None, '9')),
        ('dbs[]', (None, '12')),
        ('dbs[]', (None, '25')),
        ('dbs[]', (None, '26')),
        ('dbs[]', (None, '27')),
        ('dbs[]', (None, '35')),
        ('dbs[]', (None, '41'))
    )
    response = requests.post(url, files=files)

    soup = BeautifulSoup(response.text, 'html.parser')

    for br in soup.find_all("br"):
        br.replace_with("\n")

    result = soup.find('div', attrs={'class': 'result'})

    similarity_info = result.find('div', attrs={'class': 'resultsimilarityinfo'})
    if not similarity_info or float(similarity_info.get_text()[0:5]) < 80.0:
        return [Plain('暂时无法找到原图信息')]

    result_image_url = result.find('img')['src']
    title = "{}".format(result.find('div', attrs={'class': 'resulttitle'}).get_text())
    source_info = "{}".format(result.find('div', attrs={'class': 'resultcontentcolumn'}).get_text())
    link = result.find('div', attrs={'class': 'resultcontentcolumn'}).find('a')
    link = link['href'] if link else ''

    return [Image(url=result_image_url), Plain(title + source_info + link)]
