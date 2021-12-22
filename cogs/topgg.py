from discord.ext.commands import Cog, command
from os import environ
from logging import config, getLogger
import topgg
from handlers import MailHandler

config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())

class TopGG(Cog):
    def __init__(self, Bot):
        self.votes = {}
        self.Bot = Bot
        dbltoken = environ.get('DBLTOKEN')
        Bot.topgg = topgg.DBLClient(Bot, dbltoken)
        Bot.topgg_webhook = topgg.WebhookManager(Bot).dbl_webhook("/dblwebhook", 'log')
        Bot.topgg_webhook.run(5000)
        logger.info(f"{__name__} Cog has initialized")
        
    @command()
    async def vote(self, ctx):
        print(self.votes)
    
    @Cog.listener()
    async def on_dbl_vote(self, data):
        """An event that is called whenever someone votes for the bot on Top.gg."""
        print(f"Received a vote:\n{data}")
        if data["type"] == "test":
            # this is roughly equivalent to
            # `return await on_dbl_test(data)` in this case
            return self.Bot.dispatch("dbl_test", data)
        if data['type'] == 'vote':
            self.votes[data['user']] = {
                'vote': True,
                'claim': False
            }

        print(f"Received a vote:\n{data}")

def setup(Bot):
    Bot.add_cog(TopGG(Bot))