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

def setup(Bot):
    Bot.add_cog(Casino(Bot))