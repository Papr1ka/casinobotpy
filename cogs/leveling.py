import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Cog
from database import db
from models.to_update import To_update
from logging import config, getLogger
from handlers import MailHandler

from random import randint


config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())


class Leveling(Cog):

    leveling_table = {
        'message': 10
    }
    timing = 60

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and not message.is_system():
            user = (message.guild.id, message.author.id)
            self.queue.add(user)
    
    
    async def update_users(self):
        while True:
            await asyncio.sleep(self.timing)
            q = self.queue.get()
            await db.update_many([
                [i[0], i[1], {'$inc': {'exp': self.leveling_table['message'] * q[i], 'messages': 1}}] for i in q
            ])



    def __init__(self, Bot):
        self.Bot = Bot
        self.Bot.loop.create_task(self.update_users())
        self.queue = To_update()
        logger.info(f"{__name__} Cog has initialized")



def setup(Bot):
    Bot.add_cog(Leveling(Bot))