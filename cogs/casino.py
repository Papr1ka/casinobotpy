from os import error, name
from re import X
from typing_extensions import final

from handlers import MailHandler
import discord
from discord.ext import commands
from logging import config, getLogger, log
from main import db
from models.rulet import Rulet
from asyncio import sleep
import models.errors as errors
from cogs.error_handler import ErrorHandler


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
        'на число': ["на " + i.__str__() for i in range(0, 37)]
    }

    __messages = {} #{'message': discord.Message, 'author': str, 'bet_type': int, 'bet': int, 'bet_type_type': int}

    __bet_kf = {
        '⏬': -1000,
        '🔽': -100,
        '➖': -10,
        '➕': 10,
        '🔼': 100,
        '⏫': 1000,
    }
    __min_bet = 100
    __max_bet = 5000

    __vnumbers = {
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣',
        '0': '0️⃣',
    }

    __vcolors = {
        'red': '🟥',
        'black': '⬛️',
        'null': '⬜️'
    }
    
    __paddings = {
        1: (27, 27), #14, 11
        2: (18, 17),
        3: (23, 23),
        4: 74,
        5: 42,
        6: (27, 27)
    }

    def __init__(self, Bot): 
        self.Bot = Bot
        logger.info(f"{__name__} Cog has initialized")
    
    def __set_bet(self, money, increase, limit):
        sm = money + increase
        if sm > limit:
            return limit
        if sm > self.__max_bet:
            return self.__max_bet
        elif sm < self.__min_bet:
            return self.__min_bet
        else:
            return sm
    
    async def __emoji_handler(self, payload):
        e = payload.emoji.__str__()
        msg = self.__messages[payload.message_id]
        if msg['author_id'] != payload.user_id:
            return
        message = msg['message']
        msg['author_money'] = db.fetch_user(guild_id=payload.guild_id, user_id=payload.user_id)['money']
        embed = embed = discord.Embed(
            title = "Рулетка",
            colour = discord.Colour.random()
        )
        embed._fields = self.__rulet_fields
        embed.set_image(url='https://game-wiki.guru/content/Games/ruletka-11-pole.jpg')
        if e == "⬅️":
            logger.debug('editing bet_type: -1')
            msg['bet_type'] = (msg['bet_type'] - 1) % self.__bets_type_len
            msg['choice'] = False
        elif e == "➡️":
            logger.debug('editing bet_type: +1')
            msg['bet_type'] = (msg['bet_type'] + 1) % self.__bets_type_len
            msg['choice'] = False
        elif e == "🔳":
            logger.debug('editing bet_type_type')
            msg['bet_type_type'] = (msg['bet_type_type'] + (1 if msg['choice'] else 0)) % self.__bets[self.__bets_type[msg['bet_type']]].__len__()
            msg['choice'] = True
        elif e in ('⏬', '🔽', '➖', '➕', '🔼', '⏫'):
            logger.debug('editing money')
            msg['bet'] = self.__set_bet(msg['bet'], self.__bet_kf[e], msg['author_money'])
        else:
            if not msg['choice']:
                logger.debug(f'{msg["author"]}, did not choose bet type')
                await ErrorHandler.on_error(ctx=message.channel, error = errors.NotSelectedBetType(f'{msg["author"]}, не выбран тип ставки'))
            else:
                await self.__roll(msg)



        bet_type = self.__bets_type[msg['bet_type']] if not msg['choice'] else self.__bets[self.__bets_type[msg['bet_type']]][msg['bet_type_type']]
        self.__messages[message.id] = msg
        description = self.__format_description(msg['mobile'], msg['author'], msg['bet'], bet_type=bet_type)
        embed.description = description
        await message.edit(embed=embed)


    def __getspaces(self, on_mobile: bool, bet_type_len: int, spin: bool):
        if on_mobile:
            if spin:
                starts = self.__paddings[6]
            else:
                starts = self.__paddings[1]
        else:
            if spin:
                starts = self.__paddings[3]
            else:
                starts = self.__paddings[2]
        diff = bet_type_len - 6
        if diff % 2 == 0:
            return (starts[0] - diff // 2, starts[1] - diff // 2)
        else:
            return (starts[0] - diff // 2  - 1, starts[1] - diff // 2)
    
    def __format_description(self, on_mobile, name, money, bet_type = "Ставки", spin = False):
        spaces = self.__getspaces(on_mobile, bet_type.__len__(), spin)
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
        money = user['money']
        if money < self.__min_bet:
            raise errors.NotEnoughMoney(f'{ctx.author.name}, недостаточно средств')

        embed = discord.Embed(
            title = "Рулетка",
            description = self.__format_description(ctx.author.is_on_mobile(), ctx.author.name, self.__min_bet.__str__()),
            colour = discord.Colour.random()
        )
        embed._fields = self.__rulet_fields
        embed.set_image(url='https://game-wiki.guru/content/Games/ruletka-11-pole.jpg')
        message = await ctx.send(embed=embed)
        self.__messages[message.id] = {
            'message': message,
            'author': ctx.author.name,
            'bet_type': 0,
            'bet': self.__min_bet,
            'bet_type_type': 0,
            'author_id' : ctx.author.id,
            'choice': False,
            'mobile': ctx.author.is_on_mobile(),
            'author_money': money
        }
        for emoji in self.__rulet_emojis:
            await message.add_reaction(emoji)
    
    def __visualize_number(self, number):
        out = '0️⃣' if number < 10 else ''
        for i in number.__str__():
            out += self.__vnumbers[i]
        return out
    
    async def __roll(self, msg):
        message = msg['message']
        channel = message.channel
        padding = self.__paddings[4] if not msg['mobile'] else self.__paddings[5]
        step = 9 if not msg['mobile'] else 7
        bet_type = self.__bets_type[msg['bet_type']] if not msg['choice'] else self.__bets[self.__bets_type[msg['bet_type']]][msg['bet_type_type']]
        description = self.__format_description(msg['mobile'], msg['author'], msg['bet'], bet_type=bet_type)
        embed = discord.Embed()
        game = Rulet(step=step)
        rolls = game.spin()
        embed.add_field(name=f"```{'♥️':-^{padding}}```", value='```elixir\n' + '  '.join([self.__visualize_number(i) for i in next(rolls)]) + '\n' + '  '.join([self.__vcolors[game.check(i)[0]] * 2 for i in next(rolls)]) + '```')
        description = self.__format_description(msg['mobile'], msg['author'], msg['bet'], bet_type=bet_type, spin=True)
        embed.description = description
        message = await channel.send(embed=embed)
        for i in game.spin():
            final = i
            embed.clear_fields()
            embed.add_field(name=f"```{'♥️':-^{padding}}```", value='```elixir\n' + '  '.join([self.__visualize_number(i) for i in i]) + '\n' + '  '.join([self.__vcolors[game.check(i)[0]] * 2 for i in i]) + '```')
            await sleep(1)
            await message.edit(embed=embed)
        win = step // 2
        win = game.check(final[win])
        print(win)



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