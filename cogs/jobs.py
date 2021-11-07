from collections import namedtuple
from discord.ext.commands import Cog, command, cooldown, BucketType
from discord import File, Embed, Colour
from asyncio import sleep, TimeoutError
from random import choice, randint
import random
import os
from database import db
from math import sqrt
from discord.ext.commands.errors import CommandOnCooldown

fish = namedtuple('fish', ['url', 'cost', 'chance', 'name'])
fishes = [
    fish("https://key0.cc/images/preview/111781_c674df9fa58a5ad9cc1c1d9394a5d6bc.png", 10, 0.5, 'кислотная рыба'),
    fish("https://key0.cc/images/preview/97955_e25d2bd07b16fc7e870e6d3421901d02.png", 0, 0.5, 'кости')
]

class Jobs(Cog):

    __waitingFish = lambda self: randint(1, 30)
    modifier = lambda self, level: sqrt(level)

    def __init__(self, Bot):
        self.Bot = Bot
    

    async def randomFish(self) -> fish:
        fish = random.choices(fishes, [i.chance for i in fishes])
        return fish[0]


    @command()
    @cooldown(1, 30, BucketType.member)
    async def fishing(self, ctx):
        embed = Embed(title="Закинул удочку", color=Colour.dark_theme())
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and "подсекаю" in m.content

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
        if isinstance(error, CommandOnCooldown):
            await ctx.send("У вас только 1 спиннинг!")

        


def setup(Bot):
    Bot.add_cog(Jobs(Bot))