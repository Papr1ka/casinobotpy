from discord.ext.commands import Cog, command
from discord import Embed
from database import db
from models.coin import seller, buyer, coin_prev

class Burse(Cog):
    __burse_name = 'Casino'
    def __init__(self, Bot):
        self.Bot = Bot
        self.coins = []

    @command()
    async def coins(self, ctx):
        if not self.coins:
            c = await db.get_coin('coins', coins=1)
            self.coins = [coin_prev(i['name'], i['cost']) for i in c['coins']]
        embed = Embed(title=f'Биржа: {self.__burse_name}, Валюта: {self.coins}')
        await ctx.send(embed=embed)

    @command()
    async def createCoin(self, ctx, coin_name, cost: int, size: int):
        init_seller = seller(self.Bot.user.id, self.Bot.user.name + "#" + self.Bot.user.discriminator, size)
        await db.create_coin(coin_name, cost, size, init_seller)
        await ctx.send('Монета создана!')
        self.coins.append(coin_prev(coin_name, cost))
    
    @command()
    async def buy(self, ctx, coin_name, size):
        member = ctx.author
        b = buyer(member.id, member.name + "#" + member.discriminator, size)
        sellers = db.get_coin(coin_name, sellers=1)


def setup(Bot):
    Bot.add_cog(Burse(Bot))