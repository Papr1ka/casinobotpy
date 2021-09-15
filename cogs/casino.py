from handlers import MailHandler
from main import db
from models.rulet import Rulet
import models.errors as errors
from cogs.error_handler import ErrorHandler

import discord
from discord.ext import commands
from logging import config, getLogger
from asyncio import sleep
import time


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

    __messages = {} #{message_id: {'message': discord.Message, 'author': str, 'bet_type': int, 'bet': int, 'bet_type_type': int, 'author_id': int, 'choice': bool, 'mobile': bool, 'author_money': int, 'guild_id': int, 'last_use': time.time}}
    __games = {
        #{'channel_id': []}
    }
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
    __max_games = 2
    __sleep = 300

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
        game_over = False
        e = payload.emoji.__str__()
        try:
            msg = self.__messages[payload.message_id]
        except:
            channel = self.Bot.get_channel(payload.channel_id)
            await ErrorHandler.on_error(channel=channel, error=errors.BadGamesession("Сессия устарела"))
            msg = await channel.fetch_message(payload.message_id)
            await msg.delete(delay=1)
        else:
            if msg['author_id'] != payload.user_id:
                return
            message = msg['message']
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
                    await ErrorHandler.on_error(channel=message.channel, error=errors.NotSelectedBetType(f'{msg["author"]}, не выбран тип ставки'))
                else:
                    if msg['author_money'] >= msg['bet']:
                        await self.__roll(msg)
                    else:
                        game_over = True
                        await ErrorHandler.on_error(channel=message.channel, error=errors.NotEnoughMoney(f'{msg["author"]}, недостаточно средств'))

            if game_over:
                bet_type = 'Game Over!'
                msg['bet'] = msg['author_money']
            else:
                bet_type = self.__bets_type[msg['bet_type']] if not msg['choice'] else self.__bets[self.__bets_type[msg['bet_type']]][msg['bet_type_type']]
            msg['last_use'] = time.time()
            self.__messages[message.id] = msg
            description = self.__format_description(msg['mobile'], msg['author'], msg['bet'], bet_type=bet_type)
            embed.description = description
            await message.edit(embed=embed)
            if game_over:
                await self.__end_games([message.id])
                await sleep(ErrorHandler.getDelay())
                await message.delete()

    async def __end_games(self, games):
        logger.debug('__end_game')
        for game in games:
            self.__messages.pop(game)
        logger.debug('removed bad games')
    
    async def __is_bad_game(self):
        while not self.Bot.is_closed():
            que = []
            logger.debug("__is_bad_game")
            t = time.time()
            for id in self.__messages:
                if t - self.__messages[id]['last_use'] >= self.__sleep:
                    que.append(id)
            await self.__end_games(que)
            await sleep(self.__sleep)

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
            'author_money': money,
            'guild_id': ctx.guild.id,
            'last_use': time.time()
        }
        for emoji in self.__rulet_emojis:
            await message.add_reaction(emoji)
    
    def __visualize_number(self, number):
        out = '0️⃣' if number < 10 else ''
        for i in number.__str__():
            out += self.__vnumbers[i]
        return out
    
    def __get_win(self, bet_type_type, win, number):
        if bet_type_type in self.__bets['на цвет']:
            if bet_type_type == "на красное":
                return {'win': win[0] == "red", 'kf': 2}
            return {'win': win[0] == "black", 'kf': 2}
        elif bet_type_type in self.__bets['на чётность']:
            if bet_type_type == "на чётное":
                return {'win': win[1] == "even", 'kf': 2}
            return {'win': win[1] == "odd", 'kf': 2}
        elif bet_type_type in self.__bets['на половину']:
            if bet_type_type == "на 1-18":
                return {'win': 1 <= number <= 18, 'kf': 2}
            return {'win': 19 <= number <= 36, 'kf': 2}
        elif bet_type_type in self.__bets['на линию']:
            return {'win': int(bet_type_type[6]) == win[2], 'kf': 3}
        elif bet_type_type in self.__bets['на дюжину']:
            return {'win': (int(bet_type_type[7]) - 1) * 12 < number <= int(bet_type_type[7]) * 12, 'kf': 3}
        elif bet_type_type in self.__bets['на число']:
            return {'win': int(bet_type_type[3:]) == number, 'kf': 36}
        return {'win': False, 'kf': 0}
    
    def __format_footer(self, bet, win):
        if win['win']:
            return f"вы выиграли {bet * win['kf']}$"
        return f"вы проиграли {bet}$"
        
    def __can_roll(self, channel_id):
        try:
            games = self.__games[channel_id]
        except KeyError:
            self.__games[channel_id] = []
            return True
        else:
            if len(games) >= self.__max_games:
                return False
            return True
    
    def __remove_games(self, channel_id, game_id):
        self.__games[channel_id].remove(game_id)
        if self.__games[channel_id].__len__() == 0:
            self.__games.pop(channel_id)


    async def __roll(self, msg):
        message = msg['message']
        channel = message.channel
        if not self.__can_roll(channel.id):
            await ErrorHandler.on_error(channel, errors.TooManyGames('Ставки сделаны, приходите позже, или испольуйте другой канал'))
        else:
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
            self.__games[channel.id].append(message.id)
            for i in game.spin():
                final = i
                embed.clear_fields()
                embed.add_field(name=f"```{'♥️':-^{padding}}```", value='```elixir\n' + '  '.join([self.__visualize_number(i) for i in i]) + '\n' + '  '.join([self.__vcolors[game.check(i)[0]] * 2 for i in i]) + '```')
                await sleep(1)
                await message.edit(embed=embed)

            win_ind = step // 2
            win = game.check(final[win_ind])
            win = self.__get_win(self.__bets[self.__bets_type[msg['bet_type']]][msg['bet_type_type']], win, final[win_ind])
            increase = msg['bet'] * (win['kf'] - 1 if win['win'] else -1)
            db.update_user(guild_id=msg['guild_id'], user_id=msg['author_id'], money=increase)
            msg['author_money'] += increase
            self.__messages[msg['message'].id] = msg
            embed.set_footer(text=self.__format_footer(msg['bet'], win))
            await message.edit(embed=embed)
            self.__remove_games(channel.id, message.id)


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
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.Bot.loop.create_task(self.__is_bad_game())
    


def setup(Bot):
    Bot.add_cog(Casino(Bot))