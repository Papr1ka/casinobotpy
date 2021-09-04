from pymongo import MongoClient, database
from logging import config, getLogger, log
from pymongo.errors import CollectionInvalid
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