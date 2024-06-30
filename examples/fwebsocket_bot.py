import sys

sys.path.append("..")
sys.path.append(".")

from mirai_onebot import Bot
from mirai_onebot.adapters import ForwardWebsocketAdapter
from mirai_onebot.event.group_event import MessageGroupEvent

bot = Bot(
    adapter=ForwardWebsocketAdapter(uri="ws://127.0.0.1:8081", access_token="test")
)


@bot.on(MessageGroupEvent)
async def handler(event: MessageGroupEvent):
    print(event)


bot.run()
