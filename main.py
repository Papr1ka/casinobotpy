import discord
from discord.ext import commands
from discord import Intents
import os
from logging import config, getLogger
from database import db
from handlers import MailHandler
import logging


config.fileConfig('./logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())
logger.info('starting...')
logging.getLogger('discord').setLevel('WARNING')
logging.getLogger('requests').setLevel('WARNING')
logging.getLogger('urllib3').setLevel('WARNING')
logging.getLogger('aiohttp').setLevel('WARNING')
logging.getLogger('asyncio').setLevel('WARNING')
logging.getLogger('PIL').setLevel('WARNING')



Token = os.environ.get("TOKEN")
Bot = commands.Bot(command_prefix = "=", intents = Intents.all())

@Bot.event
async def on_ready():
    logger.info("bot is started")


@Bot.event
async def on_guild_join(guild):
    logger.info(f"bot joined guild: region - {guild.region} | name - {guild.name} | members - {guild.member_count}")
    await db.create_document(str(guild.id))
    await db.insert_many(guild.id, [member.id for member in guild.members])

@Bot.event
async def on_guild_remove(guild):
    logger.info(f"bot removed from guild: {guild.region} | {guild.name} | {guild.member_count}")
    await db.delete_document(str(guild.id))


logger.debug("loading extensions...")
Bot.load_extension("cogs.casino")
Bot.load_extension("cogs.error_handler")
Bot.load_extension("cogs.leveling")
Bot.load_extension("cogs.user_stats")
logger.debug("loading complete")

Bot.run(Token)