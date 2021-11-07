from os import name
from discord.ext.commands import Cog, command
from discord.ext.commands.core import check
from database import db
from discord import Embed
from discord.colour import Colour
from models.shop import item

from models.shop import Item


class Shop(Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @command()
    async def shop(self, ctx):
        shop = await db.fetch_user(ctx.guild.id, ctx.guild.id, items=1)
        shop = shop['items']
        embed = Embed(title='Магазин', color=Colour.dark_theme())
        if not shop:
            embed.description = "В магазине вашего сервера нет товаров, обратитесь к администратору!"
        for i in shop:
            embed.add_field(name = str(i['cost']) + '$   |  ' + i['name'], value=i['description'], inline=False)
        await ctx.send(embed=embed)
    
    async def wait_for(self, event: str, check, timeout=60):
        try:
            return await self.Bot.waif_for(event, timeout=timeout, check=check)
        except TimeoutError:
            return None

    
    @command()
    async def add_item(self, ctx):
        item_opts = []
        embed = Embed(
            title='лавка',
            color = Colour.dark_theme()
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.content and m.author.id == ctx.author.id and ctx.guild.id == m.guild.id
        
        message = await self.wait_for('message', check=check)
        if message is None:
            embed = Embed(title="Команда сброшена", color=Colour.dark_theme())
            await ctx.send(embed=embed)
        else:
            pass




def setup(Bot):
    Bot.add_cog(Shop(Bot))
