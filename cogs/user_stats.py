from discord.ext.commands import Cog, command, guild_only
from discord import Member, Embed, File, Colour
from discord.ext.commands import is_owner, has_permissions
from logging import config, getLogger
from os import remove

from models.user_model import UserModel
from models.card import Card
from models.errors import NotEnoughMoney, InvalidUser
from database import db
from handlers import MailHandler

config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())



class UserStats(Cog):

    def __init__(self, Bot):
        self.Bot = Bot
        logger.info(f"{__name__} Cog has initialized")
    
    @command(
        usage="`=status @(user)`",
        help="Получить карточку пользователя"
    )
    @guild_only()
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
        else:
            user['role_color'] = role.colour.to_rgb()
        user['avatar'] = member.avatar_url_as(format='webp', size=256).__str__()
        user['username'] = member.name
        user['discriminator'] = member.discriminator
        card = await Card(user).render_get()
        await ctx.send(file=File('./' + card))
        remove('./' + card)
    
    async def __update_level(self, guild_id, user_id, exp, level):
        money = UserModel.only_exp_to_level(level - 1)
        await db.update_user(guild_id, user_id, {'$inc': {'money': money}, '$set': {'exp': exp, 'level': level}})
    
    @command(
        usage="`=stats @(user)`",
        help="Получить статистику пользователя"
    )
    @guild_only()
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
    
    @command(
        usage="`=theme`",
        help="Изменить тему для карточки пользователя на противоположную (light / dark)"
    )
    @guild_only()
    async def theme(self, ctx):
        theme = await db.fetch_user(ctx.guild.id, ctx.author.id, color=1)
        theme = theme['color']
        if theme == 'dark':
            theme = 'light'
        else:
            theme = 'dark'
        await db.update_user(ctx.guild.id, ctx.author.id, {'$set': {'color': theme}})
        embed = Embed(
            title=f'Тема установлена на {theme.upper()}',
            color=Colour.dark_theme()
        )
        await ctx.reply(embed=embed)
    
    @command(
        usage="`=custom [описание]`",
        help="Изменить описание для карточки пользователя"
    )
    @guild_only()
    async def custom(self, ctx, *args):
        custom = ' '.join(args)
        if len(custom) > 0:
            custom = custom[:19]
        else:
            custom = UserModel.get_custom()
        await db.update_user(ctx.guild.id, ctx.author.id, {'$set': {'custom': custom}})
        title = f'Описание установлена на {custom}'
        embed = Embed(
            title=title,
            color=Colour.dark_theme()
        )
        await ctx.reply(embed=embed)
    
    async def transaction(self, fromaddr, toaddr, amount: int):
        """
        fromaddr: (guild.id, member.id),
        toaddr: (guild.id, member.id),
        amount: int
        """
        query = [
            [fromaddr[0], fromaddr[1], {'$inc': {'money': -amount}}],
            [toaddr[0], toaddr[1], {'$inc': {'money': amount}}]
        ]
        await db.update_many(query)

    @command(
        usage="`=pay @[user] [сумма]`",
        help="Перевести сумму денег со своего счёта на счёт пользователя"
    )
    @guild_only()
    async def pay(self, ctx, member: Member, amount: int):
        if not member is None:
            from_wallet = await db.fetch_user(ctx.guild.id, ctx.author.id, money=1)
            from_wallet = from_wallet['money']
            if amount <= from_wallet:
                await self.transaction((ctx.guild.id, ctx.author.id), (member.guild.id, member.id), amount)
                embed = Embed(title=f"`{amount}$` переведено на счёт {member.nick if member.nick else member.name}")
                await ctx.send(embed=embed)
            else:
                raise NotEnoughMoney(f'{(ctx.author.nick if not ctx.author.nick is None else ctx.author.name) + "#" + ctx.author.discriminator}, недостаточно средств')
        else:
            raise InvalidUser('Некорректный адресат')
    
    @command(
        usage="`=give @[user] [сумма]`",
        help="Перевести сумму денег на счёт пользователя",
        brief="administrator"
    )
    @has_permissions(administrator=True)
    @guild_only()
    async def give(self, ctx, member: Member, amount: int):
        if not member is None:
            await db.update_user(member.guild.id, member.id, {'$inc': {'money': amount}})
            embed = Embed(title=f"`{amount}$` переведено на счёт {member.nick if member.nick else member.name}")
            await ctx.send(embed=embed)
        else:
            raise InvalidUser('Некорректный адресат')
    
    
    @command(
        usage="`=offer [идея]`",
        help="Отправить предложение по улучшению работы бота, или внедрению новых возможностей"
    )
    async def offer(self, ctx, *, message):
        print(message)
        if message:
            owner = await self.Bot.application_info()
            await owner.owner.send(f"Предложение от {ctx.author.name}#{ctx.author.discriminator}: {message}, message_id={ctx.author.id}")
            await ctx.send(embed=Embed(title='Предложение отправлено', color=Colour.dark_theme()))
        else:
            await ctx.send(embed=Embed(title='Ваше предложение малосодержательное', color=Colour.dark_theme()))

    @command(
        usage="Знать не положено",
        help="Знать не положено"
    )
    @is_owner()
    async def reply(self, ctx, user_id: int, *, message):
        try:
            user = await self.Bot.fetch_user(user_id)
        except:
            await ctx.send(embed=Embed(title='пользователь не найден', color=Colour.dark_theme()))
        else:
            await user.send('Ответ на ваше предложение: ' + message)
            await ctx.send(embed=Embed(title='ответ отправлен', color=Colour.dark_theme()))


def setup(Bot):
    Bot.add_cog(UserStats(Bot))