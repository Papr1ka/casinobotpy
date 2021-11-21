import discord
from discord.embeds import Embed
from discord.ext import commands
from discord import Intents
import os
from logging import config, getLogger
from database import db
from handlers import MailHandler
import logging

from models.paginator import Paginator
from discord import Client
from discord_components import DiscordComponents


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
DBot = DiscordComponents(Bot)

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
    logger.info(f"bot removed from guild: region - {guild.region} | name - {guild.name} | members - {guild.member_count}")
    await db.delete_document(str(guild.id))

@Bot.event
async def on_member_join(member: discord.Member):
    await db.insert_user(member.guild.id, member.id)


@Bot.event
async def on_member_remove(member: discord.Member):
    await db.delete_user(member.guild.id, member.id)

Bot.remove_command('help')

@Bot.command()
async def help(ctx):
    e = Embed(title='test')
    for i in range(20):
        e.add_field(name='asd', value='12312')
    p = Paginator(DBot, ctx.channel, [e, e])
    await p.start()
    


def start():
    logger.debug("loading extensions...")
    Bot.load_extension("cogs.casino")
    Bot.load_extension("cogs.error_handler")
    Bot.load_extension("cogs.leveling")
    Bot.load_extension("cogs.user_stats")
    Bot.load_extension("cogs.jobs")
    Bot.load_extension("cogs.shop")
    logger.debug("loading complete")
    Bot.run(Token)

if __name__ == '__main__':
    start()