from discord.ext.commands import Cog, command
from logging import config, getLogger
from discord import Member, Embed, user, File
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
        role = member.top_role
        user['top_role'] = role.name[1:] if role.name.startswith('@') else role.name
        user['role_color'] = role.colour.to_rgb()
        user['avatar'] = member.avatar_url.__str__()
        user['username'] = member.name
        user['discriminator'] = member.discriminator
        card = await Card(user).render_get()
        await ctx.send(file=File('./' + card))
        remove('./' + card)


def setup(Bot):
    Bot.add_cog(UserStats(Bot))