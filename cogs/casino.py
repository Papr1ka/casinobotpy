from handlers import MailHandler
import logging
import discord
from discord.ext import commands
from logging import config, getLogger
from main import db


config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())

class Casino(commands.Cog):
    
    def __init__(self, Bot): 
        self.Bot = Bot
        logger.info("casino Cog has initialized")
    
    @commands.command()
    async def roll(self, ctx):
        await ctx.send("working")

def setup(Bot):
    Bot.add_cog(Casino(Bot))