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
        pass
    
    def connect(self):
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
        return None
        """
        try:
            logger.debug(f"creating new document - {doc_name} in database {self.db.name}...")
            self.db.create_collection(doc_name)
            logger.debug(f"{doc_name} created")
        except Exception as E:
            logger.error(f"can't create new document: {E}")
    
    def delete_document(self, doc_name : str):
        """
        deleting a document in __database_name database,
        doc_name : discord.Guild.id : string - document name
        return None
        """
        try:
            logger.debug(f"deleting document - {doc_name} in database {self.db.name}...")
            self.db.drop_collection(doc_name)
            logger.debug(f"{doc_name} deleted")
        except Exception as E:
            logger.error(f"can't delete document: {E}")
    
    @Correct_ids
    def insert_user(self, guild_id, user_id):
        """
        inserting Usermodel : dict to database
        guild_id : int
        user_id : int
        return Usermodel
        """
        try:
            logger.debug(f"inserting new user...")
            user = UserModel(user_id)
            self.db[guild_id.__str__()].insert_one(user.get_json())
            logger.debug(f'inserted new user')
            return user
        except Exception as E:
            logger.error('cant insert document: {E}')
            raise Exception('cant insert document: {E}')
    
    @Correct_ids
    def fetch_user(self, guild_id, user_id):
        """
        getting Usermodel.json() : dict
        guild_id : int
        user_id : int
        return Usermodel.json()
        """
        try:
            logger.debug(f"searching user")
            user = self.db[guild_id.__str__()].find_one({'user_id': user_id})
            logger.debug(f"finded user")
            return user
        except Exception as E:
            logger.error('cant fetch document: {E}')
            raise Exception('cant fetch document: {E}')
    
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
        upd = {}
        for i in UserModel.slots:
            p = params.get(i)
            if not p is None:
                upd[i] = p
        if upd.__len__() > 0:
            self.db[guild_id.__str__()].update_one({user_id: user_id}, upd)
            logger.debug("updating user complete")
        else:
            logger.debug("updating incorrect")

db = Database()
db.connect()
