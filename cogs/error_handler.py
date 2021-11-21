import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument, MissingPermissions
import models.errors as errors
from logging import config, getLogger
from handlers import MailHandler

config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())

class ErrorHandler(commands.Cog):

    __error_embed = discord.Embed(color=discord.Colour.dark_red())
    __delete_after = 3
    
    def __init__(self, Bot):
        self.Bot = Bot
        logger.info(f"{__name__} Cog has initialized")
    
    def getDelay(self):
        return self.__delete_after
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger.debug(f'on_command_error(), {error}')
        embed = self.__error_embed
        if isinstance(error, errors.NotEnoughMoney):
            logger.debug('errors.NotEnoughMoney')
            embed.title = error.message
            await ctx.send(embed=embed, delete_after=self.__delete_after)
        elif isinstance(error, errors.InvalidUser):
            logger.debug('errors.InvalidUser')
            embed.title = error.message
            await ctx.send(embed=embed, delete_after=self.__delete_after)
        elif isinstance(error, errors.CommandCanceled):
            logger.debug('errors.CommandCanceled')
            embed.title = error.message
            await ctx.send(embed=embed, delete_after=self.__delete_after)
        elif isinstance(error, MissingRequiredArgument):
            logger.debug('errors.MissingRequiredArgument')
            embed.title = 'Пропущен параметр'
            await ctx.send(embed=embed, delete_after=self.__delete_after)
        elif isinstance(error, MissingPermissions):
            logger.debug('errors.MissingPermissions')
            embed.title = 'Недостаточно прав'
            await ctx.send(embed=embed, delete_after=self.__delete_after)



    @staticmethod
    async def on_error(channel, error):
        embed = discord.Embed(color=discord.Colour.dark_teal())
        if isinstance(error, errors.NotSelectedBetType):
            logger.debug('errors.NotSelectedBetType')
        elif isinstance(error, errors.BadGamesession):
            logger.debug('errors.BadGamesession')
        elif isinstance(error, errors.NotEnoughMoney):
            logger.debug('errors.NotEnoughMoney')
        elif isinstance(error, errors.TooManyGames):
            logger.debug('errors.TooManyGames')
        embed.title = error.message
        await channel.send(embed=embed, delete_after=ErrorHandler.__delete_after)
            
            

def setup(Bot):
    Bot.add_cog(ErrorHandler(Bot))