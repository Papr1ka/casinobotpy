from discord import Member, Embed, Intents
from discord.colour import Colour
from discord.ext.commands import Bot as Robot
from os import environ
from logging import config, getLogger
from discord.ext.commands.core import is_owner

from database import db
from handlers import MailHandler
from discord_components import DiscordComponents


import json


config.fileConfig('./logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())
logger.info('starting...')
getLogger('discord').setLevel('WARNING')
getLogger('requests').setLevel('WARNING')
getLogger('urllib3').setLevel('WARNING')
getLogger('aiohttp').setLevel('WARNING')
getLogger('asyncio').setLevel('WARNING')
getLogger('PIL').setLevel('WARNING')



Token = environ.get("TOKEN")
Bot = Robot(command_prefix = "=", intents = Intents.all())
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
async def on_member_join(member: Member):
    await db.insert_user(member.guild.id, member.id)


@Bot.event
async def on_member_remove(member: Member):
    await db.delete_user(member.guild.id, member.id)

Bot.remove_command('help')

@Bot.command()
async def help(ctx, module_command=None):
    await on_command(Bot.get_command('help'))
    modules = ('casino', 'user', 'store', 'jobs', 'admin')
    embed = Embed(color=Colour.dark_theme())
    if not module_command:
        embed.title=f"{Bot.user.name} модули"
        embed.add_field(name='Казино', value='`=help casino`', inline=True)
        embed.add_field(name='Пользовательское', value='`=help user`', inline=True)
        embed.add_field(name='Магазин', value='`=help store`', inline=True)
        embed.add_field(name='Заработок', value='`=help jobs`', inline=True)
        embed.add_field(name='Настройка', value='`=help admin`', inline=True)
    else:
        if module_command in modules:
            if module_command == 'casino':
                embed.title=f"{Bot.user.name} casino команды"
                embed.add_field(name='Рулетка', value='`=rulet`', inline=False)
                embed.add_field(name='Блэкджек', value='`=blackjack [ставка]`', inline=False)
                embed.add_field(name='Слоты', value='`=slots [ставка]`', inline=False)
                embed.add_field(name='Кости', value='`=dice [ставка] (оппонент)`', inline=False)
            elif module_command == 'user':
                embed.title=f"{Bot.user.name} user команды"
                embed.add_field(name='Статистика пользователя', value='`=stats`', inline=False)
                embed.add_field(name='Карточка пользователя', value='`=status`', inline=False)
                embed.add_field(name='Сменить тему карточки пользователя', value='`=theme`', inline=False)
                embed.add_field(name='Сменить описание карточки пользователя', value='`=custom [описание]`', inline=False)
                embed.add_field(name='Перевести деньги', value='`=pay @[пользователь] [сумма]`', inline=False)
                embed.add_field(name='Предложить идею', value='`=offer [идея]`', inline=False)
                embed.add_field(name='Инвентарь', value='`=inventory`', inline=False)
            elif module_command == 'store':
                embed.title=f"{Bot.user.name} shop команды"
                embed.add_field(name='Магазин', value='`=shop`', inline=False)
            elif module_command == 'jobs':
                embed.title=f"{Bot.user.name} jobs команды"
                embed.add_field(name='Рыбалка', value='`=fishing` | `hook` чтобы поймать', inline=False)
            elif module_command == 'admin':
                embed.title=f"{Bot.user.name} admin команды"
                embed.add_field(name='Сбросить данные пользователей', value='`=reset [exp | money | messages | games | user | shop]`', inline=False)
                embed.add_field(name='Добавить товар в магазин', value='`=add_item`', inline=False)
                embed.add_field(name='Удалить товар из магазина', value='`=remove_item`', inline=False)
                embed.add_field(name='Пополнить баланс пользователя', value='`=give @[пользователь] [сумма]`', inline=False)
            else:
                embed.title=f"Модуль не найден"
        else:
            for i in Bot.commands:
                if i.name == module_command:
                    break
            
            if i.name != module_command:
                embed.title = "Команда не найдена"
            else:
                embed.title = i.name
                embed.add_field(name='Использование', value=i.usage, inline=False)
                embed.description = i.help
                if i.brief:
                    embed.add_field(name="Полномочия", value=i.brief)
    
    await ctx.send(embed=embed)


async def on_command(command):
    print(command)


@Bot.command()
@is_owner()
async def announcement(ctx, *, annonce):
    print(annonce)
    annonce = json.loads(annonce)
    embed = Embed.from_dict(annonce)
    for guild in Bot.guilds:
        channel = guild.system_channel
        if not channel is None:
            await channel.send(embed=embed)



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