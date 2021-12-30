from discord.embeds import EmptyEmbed
from discord.ext.commands import Cog, command, has_permissions, guild_only
from discord import Embed
from discord.colour import Colour
from math import ceil

from database import db
from main import on_command
from models.paginator import Paginator
from models.errors import CommandCanceled
from models.fishing import *
from models.fishing import components as fish_components
from models.shop import shop_id, get_shop
from discord_components import DiscordComponents, component


class Shop(Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @command(
        usage="`=shop`",
        help="Магазин вашей гильдии, за добавление товаров отвечает администрация"
    )
    @guild_only()
    async def shop(self, ctx):
        await on_command(self.Bot.get_command('shop'))
        shop = await db.fetch_user(ctx.guild.id, shop_id, items=1)
        shop = shop['items']
        embed = Embed(title='Магазин', color=Colour.dark_theme())
        
        if not shop:
            embed.description = "В магазине вашей гильдии нет товаров, обратитесь к администратору!"
            await ctx.send(embed=embed)
        else:
            l = len(shop)
            
            embeds = [Embed(title='Магазин', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
            values = [[] for i in range(ceil(l / 5))]
            
            for i in range(l):
                embeds[i // 5].add_field(name = "💸 " + str(shop[i]['cost']) + '$   |  ' + shop[i]['name'], value=shop[i]['description'], inline=False)
                values[i // 5].append(shop[i]['name'])

            c_id = str(ctx.message.id)
            
            p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds, author=ctx.author, id=c_id + "pagi", values=values)
            response, inter, msg = await p.start()
            if response == "Отменить":
                await msg.delete()
                return
            
            
            items = await db.fetch_user(ctx.guild.id, shop_id, items=1)
            items = items['items']
            match = False
            for i in items:
                if i['name'] == response:
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
                await inter.edit_origin(embed=embed, components=[component.Button(style=component.ButtonStyle.blue, label="Купить", custom_id=c_id + "buy_")])
                interaction = await self.Bot.wait_for("button_click", check = lambda i: i.custom_id == c_id + "buy_" and i.user == ctx.author)

                cost = i['cost']
                    
                user_money = await db.fetch_user(ctx.guild.id, ctx.author.id, money=1, inventory=1)
                inventory = user_money['inventory']
                user_money = user_money['money']
                if user_money >= cost:
                    if i not in inventory:
                        embed = Embed(title=f"Поздравляю с покупкой, {i['name']}!", color=Colour.dark_theme())
                        await db.update_user(ctx.guild.id, ctx.author.id, {'$push': {'inventory': i}, '$inc': {'money': -cost}})
                    else:
                        embed = Embed(title=f"У вас уже есть этот товар", color=Colour.dark_theme())
                else:
                    embed = Embed(title=f"Недостатчно средств", color=Colour.dark_theme())

                await interaction.edit_origin(embed=embed, components=[])
                
            else:
                embed = Embed(title='Товар не найден', color=Colour.dark_theme())
                await inter.edit_origin(embed=embed, components=[])


    @command(
        usage="`=fshop`",
        help="Рыболовный магазин вашей гильдии"
    )
    @guild_only()
    async def fshop(self, ctx):
        await on_command(self.Bot.get_command('fshop'))
        c_id = str(ctx.message.id)
        embed = Embed(title='Магазин', color=Colour.dark_theme())
        
        components = [[component.Button(label='Удилища', style=component.ButtonStyle.blue, custom_id=c_id + "rod"),
                       component.Button(label='Водоёмы', style=component.ButtonStyle.blue, custom_id=c_id + "pon")]]
        op = await ctx.send(embed=embed, components=components)
        
        interaction = await self.Bot.wait_for("button_click", check = lambda i: (i.custom_id == c_id + "rod" or i.custom_id == c_id + "pon") and i.user == ctx.author)
        if interaction.custom_id[-1:-4:-1][::-1] == 'rod':
            shop = [rods[r] for r in fishing_shop['rods']]
            chose = "rods"
        else:
            shop = [ponds[p] for p in fishing_shop['ponds']]
            chose = "ponds"
        
        shop = shop[1:]

        await op.delete()

        l = len(shop)
        
        embeds = [Embed(title='Магазин', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
        values = [[] for i in range(ceil(l / 5))]
        for i in range(l):
            embeds[i // 5].add_field(name = "💸 " + str(shop[i].cost) + '$   |  ' + shop[i].name, value=shop[i].description, inline=False)
            values[i // 5].append(fishing_shop[chose][i + 1])

        p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds, author=ctx.author, id=c_id + "pagi", values=values)
        response, inter, msg = await p.start()
        if response == "Отменить":
            await msg.delete()
            return
        response = int(response)
  
        if chose == 'rods':
            item = rods[response]
        else:
            item = ponds[response]
            
        
        embed = Embed(title=item.name, color=Colour.dark_theme())
        embed.add_field(name='Цена', value=f"{item.cost}$", inline=False)
        embed.add_field(name='Описание', value=item.description, inline=False)
        if chose == 'rods':
            embed.add_field(name="Модификаторы", value=f"x {item.modifiers['x']} к качеству рыбы\nТочность - {item.modifiers['aim']}", inline=False)
        embed.set_image(url=item.url)
        await inter.edit_origin(embed=embed, components=[component.Button(style=component.ButtonStyle.blue, label="Купить", custom_id=c_id + "buy_")])
        interaction = await self.Bot.wait_for("button_click", check = lambda i: i.custom_id == c_id + "buy_" and i.user == ctx.author)

        cost = item.cost
            
        user_money = await db.fetch_user(ctx.guild.id, ctx.author.id, money=1, finventory=1)
        inventory = user_money['finventory']
        user_money = user_money['money']
        if user_money >= cost:
            if response not in inventory[chose]:
                embed = Embed(title=f"Поздравляю с покупкой, {item.name}!", color=Colour.dark_theme())
                await db.update_user(ctx.guild.id, ctx.author.id, {'$push': {f'finventory.{chose}': response}, '$inc': {'money': -cost}})
            else:
                embed = Embed(title=f"У вас уже есть этот товар", color=Colour.dark_theme())
        else:
            embed = Embed(title=f"Недостатчно средств", color=Colour.dark_theme())

        await interaction.edit_origin(embed=embed, components=[])


    @command(
        usage="`=cage`",
        help="Садок"
    )
    @guild_only()
    async def cage(self, ctx):
        await on_command(self.Bot.get_command('cage'))
        c_id = str(ctx.message.id)
        shop = await db.fetch_user(ctx.guild.id, ctx.author.id, finventory=1)
        cage = shop['finventory']['cage']
        ides = {
            i: cage[i] for i in range(len(cage))
        }

        l = len(cage)
        if l == 0:
            embed = Embed(title='Магазин', color=Colour.dark_theme())
            embed.description = "Вы ещё не отложили не одной рыбы в садок"
            await ctx.send(embed=embed)
            return
        
        embeds = [Embed(title='Магазин', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
        values = [[] for i in range(ceil(l / 5))]
        
        for i in range(l):
            embeds[i // 5].add_field(name = "💸 " + str(cage[i]['cost']) + '$   |  ' + cage[i]['name'], value=cage[i]['description'], inline=False)
            values[i // 5].append(i)
            
        p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds, author=ctx.author, id=c_id + "pagi3", values=values)
        response, inter, msg = await p.start()
        if response == "Отменить":
            await msg.delete()
            return
        response = int(response)
        item = ides[response]
            
        
        embed = Embed(title=item['name'], color=Colour.dark_theme())
        embed.add_field(name='Цена', value=f"{item['cost']}$", inline=False)
        embed.add_field(name='Описание', value=item['description'], inline=False)
        embed.set_image(url=item['url'])
        embed.description = f"\nВес: {item['weight']} кг\n"
        cp = "components"
        embed.description += f"\Можно разобрать: {', '.join([f'{fish_components[i].name} - {item[cp][i]}' for i in item[cp]])}\n"
        await inter.edit_origin(embed=embed, components=[[
            component.Button(style=component.ButtonStyle.green, label="Продать", custom_id=c_id + "sell"),
            component.Button(label="Разобрать", style=component.ButtonStyle.green, custom_id=c_id + "disa")]])
        interaction = await self.Bot.wait_for("button_click", check = lambda i: (i.custom_id == c_id + "sell" or i.custom_id == c_id + "disa") and i.user == ctx.author)

        if interaction.custom_id == c_id + "sell":
            cost = item['cost']
            embed = Embed(title=f"Продано: {item['name']} за `{item['cost']}$`", color=Colour.dark_theme())
            await db.update_user(ctx.guild.id, ctx.author.id, {'$pull': {f'finventory.cage': item}, '$inc': {'money': cost}})
        else:
            await db.update_user(ctx.guild.id, ctx.author.id, {'$inc': {f'finventory.components.{i}': item['components'][i] for i in item['components']}, '$pull': {f'finventory.cage': item}})
            embed = Embed(title=f"Рыба разобрана, получено: {', '.join([f'{fish_components[i].name} - {item[cp][i]}' for i in item[cp]])}", color=Colour.dark_theme())

        await interaction.edit_origin(embed=embed, components=[])



    @command(
        usage="`=workshop`",
        help="Мастерская вашей гильдии"
    )
    @guild_only()
    async def workshop(self, ctx):
        await on_command(self.Bot.get_command('workshop'))
        c_id = str(ctx.message.id)
        embed = Embed(title='Мастерская', color=Colour.dark_theme())
        
        custom_shop = [custom_rods[i] for i in custom_rods]
        
        fcomponents = await db.fetch_user(ctx.guild.id, ctx.author.id, finventory=1)
        fcomponents = fcomponents['finventory']['components']
        
        l = len(custom_shop)
        materials = "Инвентарь:\n"
        pr = ", ".join([f'{fish_components[i].re} - {fcomponents[i]}' for i in fcomponents])
        materials += pr if pr != "" else "Пусто"
        embeds = [Embed(title='Мастерская', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
        values = [[] for i in range(ceil(l / 5))]
        for i in range(l):
            embeds[i // 5].add_field(name=custom_shop[i].name + '  |  ' + ", ".join([f'{i[0].re} - {i[1]}' for i in custom_shop[i].cost]), value=custom_shop[i].description, inline=False)
            embeds[i // 5].description = materials
            values[i // 5].append(i + 1000)

        p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds, author=ctx.author, id=c_id + "pagi", values=values)
        response, inter, msg = await p.start()
        if response == "Отменить":
            await msg.delete()
            return
        response = int(response)
  
        rod = custom_rods[response]
        
        embed = Embed(title=rod.name, color=Colour.dark_theme())
        embed.description = "Инвентарь:\n" + ", ".join([f'{fish_components[i].name} - {fcomponents[i]}' for i in fcomponents])
        embed.add_field(name='Необходимые материалы', value=", ".join([f'{i[0].name} - {i[1]}' for i in rod.cost]), inline=False)
        embed.add_field(name='Описание', value=rod.description, inline=False)
        embed.add_field(name="Модификаторы", value=f"x {rod.modifiers['x']} к качеству рыбы\nТочность - {rod.modifiers['aim']}", inline=False)
        embed.set_image(url=rod.url)
        await inter.edit_origin(embed=embed, components=[component.Button(style=component.ButtonStyle.blue, label="Собрать", custom_id=c_id + "buy_")])
        interaction = await self.Bot.wait_for("button_click", check = lambda i: i.custom_id == c_id + "buy_" and i.user == ctx.author)

        finventory = await db.fetch_user(ctx.guild.id, ctx.author.id, finventory=1)
        finventory = finventory['finventory']
        user_components = finventory['components']
        
        can_pay = True
        
        for comp, col in rod.cost:
            try:
                if user_components[comp.id] < col:
                    can_pay = False
                    break
            except KeyError:
                can_pay = False
                break
        
        if can_pay:
            if response not in finventory['rods']:
                embed = Embed(title=f"{rod.name} собран!", color=Colour.dark_theme())
                await db.update_user(ctx.guild.id, ctx.author.id, {'$push': {f'finventory.rods': response}, '$inc': {f'finventory.components.{i[0].id}': -i[1] for i in rod.cost}})
            else:
                embed = Embed(title=f"У вас уже есть этот товар", color=Colour.dark_theme())
        else:
            embed = Embed(title=f"Недостатчно материалов", color=Colour.dark_theme())

        await interaction.edit_origin(embed=embed, components=[])

    @command(
        usage="`=add_item`",
        help='Добавление товара в магазин гильдии. Активируйте команду и следуйте инструкциям в генераторе товара',
        brief='administrator'
    )
    @guild_only()
    @has_permissions(administrator=True)
    async def add_item(self, ctx):
        await on_command(self.Bot.get_command('add_item'))
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
            items = await db.fetch_user(ctx.guild.id, shop_id, items=1)
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
        
        await db.update_user(ctx.guild.id, shop_id, {'$push': {'items': item_opts}})


    @command(
        usage="`=remove_item [название предмета]`",
        help="Удаление предмета из магазина гильдии",
        brief='administrator'
    )
    @guild_only()
    @has_permissions(administrator=True)
    async def remove_item(self, ctx, *, name):
        await on_command(self.Bot.get_command('remove_item'))
        if not name:
            embed = Embed(title='Товар не найден', color=Colour.dark_theme())
        else:
            items = await db.fetch_user(ctx.guild.id, shop_id, items=1)
            items = items['items']
            match = False
            for i in items:
                if i['name'] == name:
                    match = True
                    break
            if match:
                embed = Embed(title='Товар удалён', color=Colour.dark_theme())
                await db.update_user(ctx.guild.id, shop_id, {'$pull': {'items': {'name': name}}})
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
        await on_command(self.Bot.get_command('reset'))
        embed = Embed(color=Colour.dark_theme())
        if object == 'shop':
            await db.delete_user(ctx.guild.id, shop_id)
            await db.create_shop(ctx.guild.id)
            embed.title = 'Магазин обнулён'
        elif object == 'exp':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': shop_id}}, {'$set': {'exp': 0, 'level': 1}})
            embed.title = 'уровни пользователей обнулены'
        elif object == 'money':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': shop_id}},  {'$set': {'money': 1000}})
            embed.title = 'деньги пользователей обнулены'
        elif object == 'messages':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': shop_id}}, {'$set': {'messages': 0}})
            embed.title = 'сообщения пользователей обнулены'
        elif object == 'games':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': shop_id}}, {'$set': {'games': 0}})
            embed.title = 'игры пользователей обнулены'
        elif object == 'user':
            await db.update_guild(ctx.guild.id, {'_id': {'$ne': shop_id}}, {'$set': {'exp': 0, 'level': 1, 'money': 1000, 'messages': 0, 'games': 0}})
            embed.title = 'данные пользователей обнулены'
        
        else:
            embed.title = 'Некорректный параметр'
        
        await ctx.send(embed=embed)
    
    
    @command(
        usage="`=inventory`",
        help="Ваш инвентарь, здесь вы можете продать или использовать свои предметы"
    )
    @guild_only()
    async def inventory(self, ctx):
        await on_command(self.Bot.get_command('inventory'))
        items = await db.fetch_user(ctx.guild.id, ctx.author.id, inventory=1)
        items = items['inventory']
        embed = Embed(color=Colour.dark_theme())
        if not items:
            embed.title = "В вашем инвентаре нет товаров"
            await ctx.reply(embed=embed)
        else:
            l = len(items)
            
            embeds = [Embed(title='Инвентарь', color=Colour.dark_theme()) for i in range(ceil(l / 5))]
            values = [[] for i in range(ceil(l / 5))]

            for i in range(l):
                embeds[i // 5].add_field(name = '💸 ' + str(items[i]['cost']) + '$   |  ' + items[i]['name'], value=items[i]['description'], inline=False)
                values[i // 5].append(items[i]['name'])
            c_id = str(ctx.message.id)

            p = Paginator(DiscordComponents(self.Bot), ctx.channel, embeds, author=ctx.author, id=c_id + "pagi", values=values)
            response, inter, msg = await p.start()
            if response == "Отменить":
                await msg.delete()
                return

            match = False
            for i in items:
                if i['name'] == response:
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
                await inter.edit_origin(embed=embed, components=[[
                    component.Button(style=component.ButtonStyle.blue, label="Продать", custom_id=c_id + "sell"),
                    component.Button(style=component.ButtonStyle.blue, label="Использовать", custom_id=c_id + "use_")
                    ]])
                interaction = await self.Bot.wait_for("button_click", check = lambda i: i.user == ctx.author)
                
                embed = Embed(color=Colour.dark_theme())
                
                if interaction.custom_id == c_id + 'sell':
                    cost = ceil(i['cost'] * 0.5)
                    embed.title = f"Товар продан за {cost}$"
                    await db.update_user(ctx.guild.id, ctx.author.id, {'$pull': {'inventory': {'name': i['name']}}, '$inc': {'money': cost}})
                else:
                    if not i['roles']:
                        embed.title = "Товар нельзя использовать"
                    else:
                        roles = [ctx.guild.get_role(role) for role in i['roles']]
                        try:
                            await ctx.author.add_roles(*roles)
                        except Exception as E:
                            embed.title = "Роль была удалена, или находится выше возможностей бота, сообщите администрации"
                            embed.description = "Чтобы бот мог выдать роль, она должна находиться ниже в списке ролей сервера, чем роль бота"
                        else:
                            embed.title = "Товар использован"
                            await db.update_user(ctx.guild.id, ctx.author.id, {'$pull': {'inventory': {'name': i['name']}}})
                await interaction.edit_origin(embed=embed, components=[])
                
            else:
                embed = Embed(title='Товар не найден', color=Colour.dark_theme())
                await ctx.reply(embed=embed)

def setup(Bot):
    Bot.add_cog(Shop(Bot))
