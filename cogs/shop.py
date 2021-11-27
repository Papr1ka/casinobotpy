from discord.ext.commands import Cog, command, has_permissions, guild_only
from database import db
from discord import Embed
from discord.colour import Colour
from models.paginator import Paginator
from math import ceil

from discord_components import DiscordComponents
from models.errors import CommandCanceled


class Shop(Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @command(
        usage="`=shop`",
        help="Магазин вашей гильдии, за добавление товаров отвечает администрация"
    )
    @guild_only()
    async def shop(self, ctx):
        shop = await db.fetch_user(ctx.guild.id, ctx.guild.id, items=1)
        shop = shop['items']
        embed = Embed(title='Магазин', color=Colour.dark_theme())
        
        if not shop:
            embed.description = "В магазине вашей гильдии нет товаров, обратитесь к администратору!"
            await ctx.send(embed=embed)
        else:
            l = len(shop)
            
            embeds = [Embed(title='Магазин', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
            
            for i in range(l):
                embeds[i // 5].add_field(name = str(shop[i]['cost']) + '$   |  ' + shop[i]['name'], value=shop[i]['description'], inline=False)

            
            p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds)
            await p.start()
            
    
    async def wait_for(self, event: str, check, timeout=60):
        try:
            return await self.Bot.waif_for(event, timeout=timeout, check=check)
        except TimeoutError:
            return None

    
    @command(
        usage="`=add_item`",
        help='Добавление товара в магазин гильдии. Активируйте команду и следуйте инструкциям в генераторе товара',
        brief='administrator'
    )
    @guild_only()
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
                item_opts['cost'] = int(item_opts['cost'])
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


    @command(
        usage="`=remove_item [название предмета]`",
        help="Удаление предмета из магазина гильдии",
        brief='administrator'
    )
    @guild_only()
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
        
    

    @command(
        usage="`=info [название предмета]`",
        help="Информация по предмету магазина гильдии"
    )
    @guild_only()
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
    

    @command(
        usage="`=reset [exp | money | messages | games | user | shop]`",
        help="Сброс отдельных данных гильдии (exp | money | messages | games), магазина (shop), или всех данных пользователей (user)",
        brief='administrator'
    )
    @guild_only()
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
    
    
    @command(
        usage="`=inventory (use | sell) [название предмета]`",
        help="Посмотреть инвентарь, Использовать предмет из инвентаря (use) (если возможно), продать предмет из инвентаря (sell)"
    )
    @guild_only()
    async def inventory(self, ctx, subcommand=None, *, param=None):
        items = await db.fetch_user(ctx.guild.id, ctx.author.id, inventory=1)
        items = items['inventory']
        embed = Embed(color=Colour.dark_theme())
        if not items:
            embed.title = "В вашем инвентаре нет товаров"
        else:
            if not subcommand:

                l = len(items)
                
                embeds = [Embed(title='Инвентарь', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
                
                for i in range(l):
                    embeds[i // 5].add_field(name = str(items[i]['cost']) + '$   |  ' + items[i]['name'], value=items[i]['description'], inline=False)

                
                p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds)
                await p.start()
            elif subcommand == 'use':
                match = False
                for i in items:
                    if i['name'] == param:
                        match = True
                        break
                if match:
                    if not i['roles']:
                        embed.title = "Товар нельзя использовать"
                    else:
                        roles = [ctx.guild.get_role(role) for role in i['roles']]
                        try:
                            print(roles)
                            await ctx.author.add_roles(*roles)
                        except Exception as E:
                            print(E)
                            embed.title = "Товар устарел, или роль находится выше возможностей бота"
                        else:
                            embed.title = "Товар использован"
                            await db.update_user(ctx.guild.id, ctx.author.id, {'$pull': {'inventory': {'name': param}}})        
                else:
                    embed.title = "Товар не найден"
            elif subcommand == 'sell':
                match = False
                for i in items:
                    if i['name'] == param:
                        match = True
                        break
                if match:
                    cost = ceil(i['cost'] * 0.5)
                    embed.title = f"Товар продан за {cost}$"
                    await db.update_user(ctx.guild.id, ctx.author.id, {'$pull': {'inventory': {'name': param}}})
                    await db.update_user(ctx.guild.id, ctx.author.id, {'$inc': {'money': cost}})
                else:
                    embed.title = "Товар не найден"
        if embed.title != '':
            await ctx.send(embed=embed)
                    
                
            

    
    @command(
        usage="`=buy [название предмета]`",
        help="Купить предмет из магазина вашей гильдии"
    )
    @guild_only()
    async def buy(self, ctx, *, name):
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
                
                cost = i['cost']
                
                user_money = await db.fetch_user(ctx.guild.id, ctx.author.id, money=1)
                user_money = user_money['money']
                if user_money >= cost:
                    embed = Embed(title=f"Поздравляю с покупкой, {i['name']}!", color=Colour.dark_theme())
                    await db.update_user(ctx.guild.id, ctx.author.id, {'$push': {'inventory': i}, '$inc': {'money': -cost}})
                else:
                    embed = Embed(title=f"Недостатчно средств", color=Colour.dark_theme())
            else:
                embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        await ctx.send(embed=embed)
        

def setup(Bot):
    Bot.add_cog(Shop(Bot))
