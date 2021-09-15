from handlers import MailHandler
from logging import config, getLogger, log

config.fileConfig('./logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())


class UserModel():
    __MONEY = 1000
    __EXP = 0
    __LEVEL = 1
    __VOICE = 0
    __MESSAGES = 0
    __LEVEL_COST_FORMULA = lambda level: level * (50 + level * 3)
    __slots__ = ['__user_id', '__money', '__exp', '__voice', '__messages', '__level']
    slots = [i[2:] for i in __slots__]
    def __init__(self, user_id = None):
        self.__user_id = user_id
        self.__money = self.__MONEY
        self.__voice = self.__VOICE
        self.__messages = self.__MESSAGES
        self.__exp, self.__level = self.exp_to_level(self.__EXP, self.__LEVEL)
        logger.debug('created UserModel')
    
    @classmethod
    def set_cls_field(cls, **params):
        """
        set start params
        params:
        MONEY: User start money at guild, default=1000
        EXP: User start experience at guild, default=0
        VOICE: User start time at guild voice channels, default=0
        Messages: User start messages at guild text channels, default=0
        LEVEL_FORMULA: level cost function; args=(level)
        """
        logger.info(f'new UserModel start params: {params}')
        cls.__MONEY = params.pop('MONEY', 1000)
        cls.__EXP = params.pop('EXP', 0)
        cls.__VOICE = params.pop('VOICE', 0)
        cls.__MESSAGES = params.pop('MESSAGES', 0)
        cls.__LEVEL_COST_FORMULA = params.pop('LEVEL_COST_FORMULA', lambda level: level * (50 + level * 3))
    
    def get_json(self):
        return {
            '_id': self.__user_id,
            'money': self.__money,
            'exp': self.__exp,
            'level': self.__level,
            'voice': self.__voice,
            'messages': self.__messages,
        }
    
    @staticmethod
    def exp_to_level(exp, level):
        """
        return user real exp, level
        """
        while exp >= UserModel.__LEVEL_COST_FORMULA(level):
            exp -= UserModel.__LEVEL_COST_FORMULA(level)
            level += 1
        return exp, level
