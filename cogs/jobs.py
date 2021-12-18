from collections import namedtuple
from discord.ext.commands import Cog, command, BucketType, max_concurrency, guild_only
from discord import Embed, Colour
from asyncio import TimeoutError
from random import randint, choices
from database import db
from math import sqrt
from discord.ext.commands.errors import MaxConcurrencyReached

from main import on_command

fish = namedtuple('fish', ['url', 'cost', 'chance', 'name'])
fishes = [
    fish("https://key0.cc/images/preview/111781_c674df9fa58a5ad9cc1c1d9394a5d6bc.png", 10, 0.5, 'Кислотная рыба'),
    fish("https://key0.cc/images/preview/97955_e25d2bd07b16fc7e870e6d3421901d02.png", 0, 0.5, 'Кости')
]

class Jobs(Cog):

    __waitingFish = lambda self: randint(1, 30)
    modifier = lambda self, level: sqrt(level)

    def __init__(self, Bot):
        self.Bot = Bot
    

    async def randomFish(self) -> fish:
        fish = choices(fishes, [i.chance for i in fishes])
        return fish[0]


    @command(
        usage="`=fishing` | `hook` чтобы поймать",
        help="Активируйте команду и напишите `hook`, чтобы поймать рыбу, главное сделать это вовремя"
    )
    @max_concurrency(1, BucketType.member, wait=False)
    @guild_only()
    async def fishing(self, ctx):
        await on_command(self.Bot.get_command('fishing'))
        embed = Embed(title="Закинул удочку", color=Colour.dark_theme())
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and "hook" in m.content

        try:
            message = await self.Bot.wait_for('message', timeout=self.__waitingFish(), check=check)
        except TimeoutError:
            pass
        else:
            embed = Embed(title="Рыба испугалась", color=Colour.dark_theme())
            await ctx.send(embed=embed)
            return


        embed = Embed(title="Клюёт!!!", color=Colour.dark_theme())
        await ctx.send(embed=embed)

        try:
            message = await self.Bot.wait_for('message', timeout=5, check=check)
        except TimeoutError:
            embed = Embed(title="Рыба ускользнула", color=Colour.dark_theme())
        else:
            level = await db.fetch_user(ctx.guild.id, ctx.author.id, level=1)
            level = level['level']
            fish = await self.randomFish()
            embed = Embed(title="Вы поймали рыбу!", color=Colour.dark_theme())
            embed.set_thumbnail(url=fish.url)
            income = round(fish.cost * self.modifier(level))
            embed.set_footer(text=f'Выручка: {income}$')
            if income > 0:
                await db.update_user(ctx.guild.id, ctx.author.id, {'$inc': {'money': income}})
        await ctx.send(embed=embed)

    @fishing.error
    async def on_fishing_error(self, ctx, error):
        if isinstance(error, MaxConcurrencyReached):
            await ctx.send("У вас только 1 спиннинг!")



def setup(Bot):
    Bot.add_cog(Jobs(Bot))