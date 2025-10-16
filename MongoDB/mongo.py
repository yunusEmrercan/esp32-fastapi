# MongoDB/mongo.py
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger("mongo_wrapper")

class MongoDB:
    def __init__(self, db, collection, connection_url='mongodb://localhost:27017/'):
        self.client = MongoClient(connection_url)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def find_document(self, query):
        try:
            return self.collection.find_one(query)
        except PyMongoError as e:
            logger.error(f"find_document error: {e}")
            raise

    def find_many(self, query):
        try:
            return list(self.collection.find(query))
        except PyMongoError as e:
            logger.error(f"find_many error: {e}")
            raise

    def insert_one(self, doc):
        try:
            return self.collection.insert_one(doc)
        except PyMongoError as e:
            logger.error(f"insert_one error: {e}")
            raise

    def update_one(self, query, update):
        try:
            return self.collection.update_one(query, update)
        except PyMongoError as e:
            logger.error(f"update_one error: {e}")
            raise

    def find_one_and_update(self, query, update, return_document=ReturnDocument.AFTER):
        try:
            return self.collection.find_one_and_update(query, update, return_document=return_document)
        except PyMongoError as e:
            logger.error(f"find_one_and_update error: {e}")
            raise
