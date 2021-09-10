from os import name
from handlers import MailHandler
import discord
from discord.ext import commands
from logging import config, getLogger
from main import db


config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())


class Casino(commands.Cog):
    
    def __init__(self, Bot): 
        self.Bot = Bot
        logger.info("casino Cog has initialized")
    
    def __getspaces(self, on_mobile: bool):
        return (14, 11) if on_mobile else (16, 16)
    
    def __format_description(self, on_mobile, name, money):
        spaces = self.__getspaces(on_mobile)
        description = f"{name[:spaces[0]]: <{spaces[0]}} |  Ставки  | {money: >{spaces[1]}}$"
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

        fields = [
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

        embed = discord.Embed(
            title = "Рулетка",
            description = self.__format_description(ctx.author.is_on_mobile(), ctx.author.name, user.get('money')),
            colour = discord.Colour.random()
        )
        embed._fields = fields
        embed.set_image(url='https://game-wiki.guru/content/Games/ruletka-11-pole.jpg')
        await ctx.send(embed = embed)

def setup(Bot):
    Bot.add_cog(Casino(Bot))