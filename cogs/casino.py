import discord
from discord.ext import commands
from logging import config, getLogger
from main import db

import os
print (os.getcwd())


config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)

class Casino(commands.Cog):
    
    def __init__(self, Bot): 
        self.Bot = Bot
        logger.info("casino Cog has initialized")
        user = db.insert_user(guild_id=111111111111111111, user_id=567567567567567567)
        print(user.slots)

def setup(Bot):
    Bot.add_cog(Casino(Bot))