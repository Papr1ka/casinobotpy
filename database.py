from pymongo import MongoClient
from logging import config, getLogger, log
from models.user_model import UserModel
import os

config.fileConfig('./logging.ini', disable_existing_loggers=False)
logger = getLogger(__name__)



class Database(MongoClient):

    __database_name = "casino"
    __mongo_password = os.environ.get("MONGO_PASSWORD")

    def __init__(self):
        try:
            logger.debug(f'connecting to cluster...')
            super().__init__(f"mongodb+srv://user:{self.__mongo_password}@cluster0.qbwbb.mongodb.net/{self.__database_name}?retryWrites=true&w=majority")
            logger.info(f"connected to cluster, aviable databases: {', '.join(self.database_names())}")
            logger.debug(self.server_info())
            self.db = self[self.__database_name]
            logger.info(f"connected to database: {self.__database_name}")
        except Exception as E:
            logger.critical(f"can't connect to database: {E}")
    
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
        """
        try:
            logger.debug(f"creating new document - {doc_name} in database {self.db.name}...")
            self.db.create_collection(doc_name)
            logger.debug(f"{doc_name} created")
        except Exception as E:
            logger.critical(f"can't create new document: {E}")
    
    def delete_document(self, doc_name : str):
        """
        deleting a document in __database_name database,
        doc_name : discord.Guild.id : string - document name
        """
        try:
            logger.debug(f"deleting document - {doc_name} in database {self.db.name}...")
            self.db.drop_collection(doc_name)
            logger.debug(f"{doc_name} deleted")
        except Exception as E:
            logger.critical(f"can't delete document: {E}")
    
    @Correct_ids
    def insert_user(self, guild_id, user_id):
        logger.critical(f"{guild_id}, {user_id}, {type(guild_id), type(user_id)}")
        try:
            logger.debug(f"inserting new user...")
            user = UserModel(user_id)
            self.db[str(guild_id)].insert_one(user.get_json())
            logger.debug(f'inserted new user')
        except Exception as E:
            logger.critical('cant insert document: {E}')
            raise Exception('cant insert document: {E}')
    
    @Correct_ids
    def fetch_user(self, guild_id, user_id):
        logger.critical(f"{guild_id}, {user_id}, {type(guild_id), type(user_id)}")
        try:
            logger.debug(f"searching user")
            user = self.db[f'{guild_id}'].find_one({'user_id' : user_id})
            logger.debug(f"finded user")
            return user
        except Exception as E:
            logger.critical('cant fetch document: {E}')
            raise Exception('cant fetch document: {E}')
