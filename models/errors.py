from discord.ext.commands import errors

class NotEnoughMoney(errors.CommandError):
    """
    The exception that is thrown
    when the user does not have enough
    funds to complete the transaction.
    """
    def __init__(self, message, *args):
        self.message = message
        super().__init__(message=message, *args)

class NotSelectedBetType(errors.CommandError):
    """
    pass
    """
    def __init__(self, message, *args):
        self.message = message
        super().__init__(message=message, *args)