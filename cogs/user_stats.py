from math import exp
from discord.ext.commands import Cog, command
from logging import config, getLogger
from discord import Member, Embed, embeds, user, File
from PIL import Image, ImageFont, ImageDraw, ImageChops
from io import BytesIO
from aiohttp import ClientSession as aioSession
from models.user_model import UserModel
from database import db
from handlers import MailHandler
from models.card import Card
from os import remove

config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())



class UserStats(Cog):

    def __init__(self, Bot):
        self.Bot = Bot
        logger.info(f"{__name__} Cog has initialized")
    
    @command()
    async def status(self, ctx, member: Member = None):
        if member is None:
            member = ctx.author
        user = await db.fetch_user(ctx.guild.id, member.id, exp=1, level=1, custom=1, color=1)
        exp, level, _ = UserModel.exp_to_level(user['exp'], user['level'])
        if level > user['level']:
            await self.__update_level(ctx.guild.id, member.id, exp, level)
        role = member.top_role
        user['top_role'] = role.name[1:] if role.name.startswith('@') else role.name
        if user['top_role'] == 'everyone':
            if user['color'] == 'dark':
                user['role_color'] = (255, 255, 255)
            else:
                user['role_color'] = role.colour.to_rgb()
        user['avatar'] = member.avatar_url.__str__()
        user['username'] = member.name
        user['discriminator'] = member.discriminator
        card = await Card(user).render_get()
        await ctx.send(file=File('./' + card))
        remove('./' + card)
    
    async def __update_level(self, guild_id, user_id, exp, level):
        money = UserModel.only_exp_to_level(level - 1)
        await db.update_user(guild_id, user_id, {'$inc': {'money': money}, '$set': {'exp': exp, 'level': level}})
    
    @command()
    async def stats(self, ctx, member: Member = None):
        if member is None:
            member = ctx.author
        user = await db.fetch_user(ctx.guild.id, member.id, money=1, messages=1, games=1, exp=1, level=1)
        exp, level, _ = UserModel.exp_to_level(user['exp'], user['level'])
        if level > user['level']:
            await self.__update_level(ctx.guild.id, member.id, exp, level)
        embed = Embed(title = member.name + '#' + member.discriminator)
        embed.add_field(name='Денег', value=user['money'])
        embed.add_field(name='Сообщений', value=user['messages'])
        embed.add_field(name='Игр сыграно', value=user['games'])
        embed.set_author(name='Статистика')
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)



def setup(Bot):
    Bot.add_cog(UserStats(Bot))