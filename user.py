from math import ceil

class User():
    __MONEY = 1000
    __EXP = 0
    __LEVEL = 1
    __VOICE = 0
    __MESSAGES = 0
    __LEVEL_COST_FORMULA = lambda self, level: level * (50 + level * 3)

    def __init__(self, user_id):
        self.__user_id = user_id
        self.__money = self.__MONEY
        self.__exp = self.__EXP
        self.__voice = self.__VOICE
        self.__messages = self.__MESSAGES
        self.__level = self.__LEVEL
        self.__exp_to_level()
    
    @classmethod
    def _set_cls_field(cls, **params):
        """
        set start params
        params:
        MONEY: User start money at guild, default=1000
        EXP: User start experience at guild, default=0
        VOICE: User start time at guild voice channels, default=0
        Messages: User start messages at guild text channels, default=0
        LEVEL_FORMULA: level cost function
        """
        cls.__MONEY = params.pop('MONEY', 1000)
        cls.__EXP = params.pop('EXP', 0)
        cls.__VOICE = params.pop('VOICE', 0)
        cls.__MESSAGES = params.pop('MESSAGES', 0)
        cls.__LEVEL_COST_FORMULA = params.pop('LEVEL_COST_FORMULA', lambda self, level: level * (50 + level * 3))

    @property
    def exp(self):
        return self.__exp
    
    @property
    def level_cost(self):
        return self.__LEVEL_COST_FORMULA(self.__level)
    
    @property
    def level(self):
        return self.__level
    
    @exp.setter
    def exp(self, number: int):
        self.__exp += number
        self.__exp_to_level()
    
    def __exp_to_level(self):
        while self.__exp >= self.level_cost:
            print(f"{self.__exp} / {self.level_cost}")
            self.__exp -= self.level_cost
            self.__level += 1
    
    @property
    def money(self):
        return self.__money
    
    @money.setter
    def money(self, money: int):
        self.__money += money
    
    @property
    def voice(self):
        return self.__voice
    
    @money.setter
    def voice(self, voice: int):
        self.__voice += voice
    
    @property
    def messages(self):
        return self.__messages
    
    @money.setter
    def messages(self, messages: int):
        self.__messages += messages
    


User._set_cls_field(EXP = 2999)
Bob = User(12345678)
print(f"{Bob.exp} | {Bob.level_cost} | {Bob.level}")