from os import name

from discord import emoji
from handlers import MailHandler
import discord
from discord.ext import commands
from logging import config, getLogger
from main import db


config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())


class Casino(commands.Cog):

    __rulet_fields = [
        {
            'inline': True,
            'name': 'на цвет',
            'value': 'выйгрыш 1 к 1'
        },
        {
            'inline': True,
            'name': 'на чётность',
            'value': 'выйгрыш 1 к 1'
        },
        {
            'inline': True,
            'name': 'на половину',
            'value': 'выйгрыш 1 к 1'
        },
        {
            'inline': True,
            'name': 'на дюжину',
            'value': 'выйгрыш 2 к 1'
        },
        {
            'inline': True,
            'name': 'на линию',
            'value': 'выйгрыш 2 к 1'
        },
        {
            'inline': True,
            'name': 'на число',
            'value': 'выйгрыш 35 к 1'
        }
    ]

    __rulet_emojis = [
        '⬅️',
        '🔳',
        '➡️',
        '⏬',
        '🔽',
        '➖',
        '➕',
        '🔼',
        '⏫',
        '🎰'
    ]

    __bets_type = [
        'на цвет',
        'на чётность',
        'на половину',
        'на линию',
        'на дюжину',
        'на число'
    ]

    __bets_type_len = __bets_type.__len__()

    __bets = {
        'на цвет': ['на красное', 'на чёрное'],
        'на чётность': ['на чётное', 'на нечётное'],
        'на половину': ['на 1-18', 'на 19-36'],
        'на линию': ['линия 1', 'линия 2', 'линия 3'],
        'на дюжину': ['дюжина 1', 'дюжина 2', 'дюжина 3'],
        'на число': [i.__str__() for i in range(0, 37)]
    }

    __messages = {} #{'message': discord.Message, 'author': str, 'bet_type': int, 'bet': int, 'bet_type_type': int}
    
    def __init__(self, Bot): 
        self.Bot = Bot
        logger.info("casino Cog has initialized")
    
    async def __emoji_handler(self, payload):
        e = payload.emoji.__str__()
        msg = self.__messages[payload.message_id]
        if msg['author_id'] != payload.user_id:
            return
        message = msg['message']
        embed = embed = discord.Embed(
            title = "Рулетка",
            description = self.__format_description(message.author.is_on_mobile(), msg['author'], msg['bet']),
            colour = discord.Colour.random()
        )
        embed._fields = self.__rulet_fields
        embed.set_image(url='https://game-wiki.guru/content/Games/ruletka-11-pole.jpg')
        if e == "⬅️":
            logger.debug('editing bet_type: -1')
            msg['bet_type'] = (msg['bet_type'] - 1) % self.__bets_type_len
            bet_type = self.__bets_type[msg['bet_type']]
            self.__messages[message.id] = msg
            description = self.__format_description(message.author.is_on_mobile(), msg['author'], msg['bet'], bet_type=bet_type)
            embed.description = description
            await message.edit(embed=embed)
        elif e == "➡️":
            logger.debug('editing bet_type: +1')
            msg['bet_type'] = (msg['bet_type'] + 1) % self.__bets_type_len
            bet_type = self.__bets_type[msg['bet_type']]
            self.__messages[message.id] = msg
            description = self.__format_description(message.author.is_on_mobile(), msg['author'], msg['bet'], bet_type=bet_type)
            embed.description = description
            await message.edit(embed=embed)
        elif e == "🔳":
            logger.debug('editing bet_type_type')
            msg['bet_type_type'] = (msg['bet_type_type'] + 1) % self.__bets[self.__bets_type[msg['bet_type']]].__len__()
            bet_type = self.__bets[self.__bets_type[msg['bet_type']]][msg['bet_type_type']]
            self.__messages[message.id] = msg
            description = self.__format_description(message.author.is_on_mobile(), msg['author'], msg['bet'], bet_type=bet_type)
            embed.description = description
            await message.edit(embed=embed)
    
    def __getspaces(self, on_mobile: bool, bet_type_len: int):
        starts = (14, 11) if on_mobile else (18, 17)
        diff = bet_type_len - 6
        if diff % 2 == 0:
            return (starts[0] - diff // 2, starts[1] - diff // 2)
        else:
            return (starts[0] - diff // 2  - 1, starts[1] - diff // 2)
    
    def __format_description(self, on_mobile, name, money, bet_type = "Ставки"):
        spaces = self.__getspaces(on_mobile, bet_type.__len__())
        description = f"{name[:spaces[0]]: <{spaces[0]}} |  {bet_type}  | {money: >{spaces[1]}}$"
        if not on_mobile:
            description = '```elixir\n' + description + '```'
        else:
            description = '**' + description + '**'
        return description + '\n'
    
    @commands.command()
    async def rulet(self, ctx):
        logger.debug('called command rulet')
        user = db.fetch_user(guild_id=ctx.guild.id, user_id=ctx.author.id)

        if user is None:
            user = db.insert_user(guild_id=ctx.guild.id, user_id=ctx.author.id).get_json()

        embed = discord.Embed(
            title = "Рулетка",
            description = self.__format_description(ctx.author.is_on_mobile(), ctx.author.name, '1000'),
            colour = discord.Colour.random()
        )
        embed._fields = self.__rulet_fields
        embed.set_image(url='https://game-wiki.guru/content/Games/ruletka-11-pole.jpg')
        message = await ctx.send(embed = embed)
        self.__messages[message.id] = {
            'message': message,
            'author': ctx.author.name,
            'bet_type': 0,
            'bet': 1000,
            'bet_type_type': -1,
            'author_id' : ctx.author.id
        }
        for emoji in self.__rulet_emojis:
            await message.add_reaction(emoji)
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        logger.debug('reaction added')
        if payload.emoji.__str__() in self.__rulet_emojis and not payload.member.bot:
            await self.__emoji_handler(payload)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        logger.debug('reaction removed')
        if payload.emoji.__str__() in self.__rulet_emojis:
            await self.__emoji_handler(payload)


def setup(Bot):
    Bot.add_cog(Casino(Bot))