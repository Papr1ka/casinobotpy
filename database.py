from handlers import MailHandler
from discord.errors import InvalidArgument
from pymongo import MongoClient
from logging import config, getLogger, log
from models.user_model import UserModel
import os

config.fileConfig('./logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)
logger.addHandler(MailHandler())



class Database(MongoClient):

    __database_name = "casino"
    __mongo_password = os.environ.get("MONGO_PASSWORD")

    def __init__(self):
        pass
    
    def connect(self):
        logger.debug('connecting to cluster...')
        try:
            super().__init__(f"mongodb+srv://user:{self.__mongo_password}@cluster0.qbwbb.mongodb.net/{self.__database_name}?retryWrites=true&w=majority")
            logger.info(f"connected to cluster, aviable databases: {', '.join(self.database_names())}")
            logger.debug(self.server_info())
            self.db = self[self.__database_name]
        except Exception as E:
            logger.critical(f"can't connect to database: {E}")
        else:
            logger.info(f"connected to database: {self.__database_name}")

    def Correct_ids(function):
        def wrapper(self, **kwargs):
            guild_id = kwargs.get('guild_id')
            if Database.__check_id(guild_id):
                user_id = kwargs.get('user_id')
                if Database.__check_id(user_id):
                    return function(self, **kwargs)
                logger.error(f"invalid user_id: {user_id}, {type(user_id)}, int required")
                raise ValueError(f"invalid user_id: {user_id}, {type(user_id)}, int required")
            logger.error(f"invalid guild_id: {guild_id}, {type(guild_id)}, int required")
            raise ValueError(f"invalid guild_id: {guild_id}, {type(guild_id)}, int required")
        return wrapper

    @staticmethod
    def __check_id(user_id):
        if isinstance(user_id, int) and user_id.__str__().__len__() == 18:
            return True
        else:
            return False
    
    def create_document(self, doc_name : str):
        """
        creating a  new document in __database_name database,
        doc_name : discord.Guild.id : string - document name
        return None
        """
        logger.debug(f"creating new document - {doc_name} in database {self.db.name}...")
        try:
            self.db.create_collection(doc_name)
        except Exception as E:
            logger.error(f"can't create new document: {E}")
        else:
            logger.debug(f"{doc_name} created")
    
    def delete_document(self, doc_name : str):
        """
        deleting a document in __database_name database,
        doc_name : discord.Guild.id : string - document name
        return None
        """
        logger.debug(f"deleting document - {doc_name} in database {self.db.name}...")
        try:
            self.db.drop_collection(doc_name)
        except Exception as E:
            logger.error(f"can't delete document: {E}")
        else:
            logger.debug(f"{doc_name} deleted")
    
    @Correct_ids
    def insert_user(self, guild_id, user_id):
        """
        inserting Usermodel : dict to database
        guild_id : int
        user_id : int
        return Usermodel
        """
        logger.debug("inserting new user...")
        user = UserModel(user_id)
        try:
            self.db[guild_id.__str__()].insert_one(user.get_json())
        except Exception as E:
            logger.error(f'cant insert user: {E}')
        else:
            logger.debug('inserted new user')
            return user
    
    @Correct_ids
    def fetch_user(self, guild_id, user_id):
        """
        getting Usermodel.json() : dict
        guild_id : int
        user_id : int
        return Usermodel.json()
        """
        logger.debug("searching user")
        try:
            user = self.db[guild_id.__str__()].find_one({'user_id': user_id})
        except Exception as E:
            logger.debug(f'cant fetch user: {E}')
        else:
            if user is None:
                user = self.insert_user(guild_id=guild_id, user_id=user_id)
                return user.get_json()
            logger.debug("finded user")
            return user
    
    @Correct_ids
    def update_user(self, guild_id, user_id, **params):
        """
        updating Usermodel.json() : dict
        guild_id : int
        user_id : int
        params: Usermodel.slots params
        return None
        """
        logger.debug("updating user...")
        logger.debug(f"updating: {params}")
        try:
            for p in params.keys():
                if p not in UserModel.slots:
                    raise InvalidArgument(params)
            r = self.db[guild_id.__str__()].update_one({'user_id': user_id}, {'$inc': params})
        except Exception as E:
            logger.error(f'updating user error: {E}')
        else:
            logger.debug("updating user complete")
    
    @Correct_ids
    def delete_user(self, guild_id, user_id):
        logger.debug("deleting user...")
        try:
            self.db[guild_id.__str__()].delete_one({'user_id': user_id})
        except Exception as E:
            logger.error(f"can't delete user: {E}")
        else:
            logger.debug("deleting complete")

db = Database()
db.connect()
