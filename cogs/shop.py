from os import name
from discord.ext.commands import Cog, command, has_permissions
from discord.ext.commands.core import check
from discord.ext.commands.errors import CommandError
from database import db
from discord import Embed, message
from discord.colour import Colour
from models.shop import item

from models.shop import Item
from models.paginator import Paginator
from math import ceil, cos

from discord_components import DiscordComponents
from models.errors import CommandCanceled


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
            await ctx.send(embed=embed)
        else:
            l = len(shop)
            
            embeds = [Embed(title='Магазин', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
            
            for i in range(len(shop)):
                embeds[i // 5].add_field(name = str(shop[i]['cost']) + '$   |  ' + shop[i]['name'], value=shop[i]['description'], inline=False)

            
            p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds)
            await p.start()
            
    
    async def wait_for(self, event: str, check, timeout=60):
        try:
            return await self.Bot.waif_for(event, timeout=timeout, check=check)
        except TimeoutError:
            return None

    
    @command()
    @has_permissions(administrator=True)
    async def add_item(self, ctx):
        item_opts = {}
        embed = Embed(
            title='Создание товара',
            color = Colour.dark_theme()
        )
        embed.set_footer(text='Введите название товара | `отменить` для отмены')
        main = await ctx.send(embed=embed)

        def check(m):
            return m.content and m.author.id == ctx.author.id and ctx.guild.id == m.guild.id

        async def get(item_opts, key, place):
            try:
                message = await self.Bot.wait_for('message', check=check, timeout=60)
            except TimeoutError:
                raise CommandCanceled('Команда сброшена')
            else:
                if message.content == 'отменить':
                    raise CommandCanceled('Команда сброшена')
                else:
                    if place == 'content':
                        item_opts[key] = message.content
                    else:
                        item_opts[key] = message.role_mentions
                    return item_opts
        
        
        
        name = False
        
        while name is False:
            item_opts = await get(item_opts, 'name', 'content')
            items = await db.fetch_user(ctx.guild.id, ctx.guild.id, items=1)
            items = items['items']
            unicle = True
            for i in items:
                if i['name'] == item_opts['name']:
                    unicle = False
                    embed.set_footer(text='Имя должно быть уникальным | `отменить` для отмены')
            if unicle:
                embed.title = item_opts['name']
                embed.set_footer(text='Введите цену товара | `отменить` для отмены')
                name = True
            await main.edit(embed=embed)
                
        
        cost = False
        while cost is False:
            item_opts = await get(item_opts, 'cost', 'content')
            try:
                int(item_opts['cost'])
            except ValueError:
                embed.set_footer(text='Введите цену товара [число] | `отменить` для отмены')
                await main.edit(embed=embed)
            else:
                cost = True
        
        embed.add_field(name='Цена', value=item_opts['cost'], inline=False)
        embed.set_footer(text='Введите описание товара | `отменить` для отмены')
        await main.edit(embed=embed)
        
        item_opts = await get(item_opts, 'description', 'content')
        embed.add_field(name='Описание', value=item_opts['description'], inline=False)
        embed.set_footer(text='Введите роль, выдаваемую при покупке | без @role - без роли | `отменить` для отмены')
        await main.edit(embed=embed)
        
        item_opts = await get(item_opts, 'roles', 'roles')
        if item_opts['roles']:
            embed.add_field(name='Роли', value=' '.join([role.mention for role in item_opts['roles']]), inline=False)
        else:
            embed.add_field(name='Роли', value='Нет', inline=False)
        embed.set_footer(text='Товар создан!')
        await main.edit(embed=embed)
        
        n = []
        
        for role in item_opts['roles']:
            n.append(role.id)
        
        item_opts['roles'] = n
        
        await db.update_user(ctx.guild.id, ctx.guild.id, {'$push': {'items': item_opts}})


    @command()
    @has_permissions(administrator=True)
    async def remove_item(self, ctx, *, name):
        if not name:
            embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        else:
            items = await db.fetch_user(ctx.guild.id, ctx.guild.id, items=1)
            items = items['items']
            match = False
            for i in items:
                if i['name'] == name:
                    match = True
                    break
            if match:
                embed = Embed(title='Товар удалён', color=Colour.dark_theme())
                await db.update_user(ctx.guild.id, ctx.guild.id, {'$pull': {'items': {'name': name}}})
            else:
                embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        await ctx.send(embed=embed)
        
    

    @command()
    async def info(self, ctx, *, name):
        if not name:
            embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        else:
            items = await db.fetch_user(ctx.guild.id, ctx.guild.id, items=1)
            items = items['items']
            match = False
            for i in items:
                if i['name'] == name:
                    match = True
                    break
            if match:
                embed = Embed(title=i['name'], color=Colour.dark_theme())
                embed.add_field(name='Цена', value=f"{i['cost']}$", inline=False)
                embed.add_field(name='Описание', value=i['description'], inline=False)
                roles = [ctx.guild.get_role(role) for role in i['roles']]
                if not roles:
                    embed.add_field(name='Роли', value='нет', inline=False)
                else:
                    embed.add_field(name='Роли', value=' '.join([role.mention for role in roles]), inline=False)
            else:
                embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        await ctx.send(embed=embed)
    

    @command()
    @has_permissions(administrator=True)
    async def reset(self, ctx, *, object):
        embed = Embed(color=Colour.dark_theme())
        if object == 'shop':
            await db.update_user(ctx.guild.id, ctx.guild.id, {'$set': {'items': []}})
            embed.title = 'Магазин обнулён'
        elif object == 'exp':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': ctx.guild.id}}, {'$set': {'exp': 0, 'level': 1}})
            embed.title = 'уровни пользователей обнулены'
        elif object == 'money':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': ctx.guild.id}},  {'$set': {'money': 1000}})
            embed.title = 'деньги пользователей обнулены'
        elif object == 'messages':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': ctx.guild.id}}, {'$set': {'messages': 0}})
            embed.title = 'сообщения пользователей обнулены'
        elif object == 'games':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': ctx.guild.id}}, {'$set': {'games': 0}})
            embed.title = 'игры пользователей обнулены'
        elif object == 'user':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': ctx.guild.id}}, {'$set': {'exp': 0, 'level': 1, 'money': 1000, 'messages': 0, 'games': 0}})
            embed.title = 'данные пользователей обнулены'
        
        else:
            embed.title = 'Некорректный параметр'
        
        await ctx.send(embed=embed)
        

def setup(Bot):
    Bot.add_cog(Shop(Bot))
