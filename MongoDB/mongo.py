# MongoDB/mongo.py
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger("mongo_wrapper")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'))
logger.addHandler(ch)

class MongoDB:
    def __init__(self, db_name, collection_name, connection_url='mongodb://localhost:27017/'):
        self.client = MongoClient(connection_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    # Tek bir belge bul
    def find_document(self, query: dict):
        try:
            return self.collection.find_one(query)
        except PyMongoError as e:
            logger.error(f"find_document error: {e}")
            raise

    # Birden fazla belge bul
    def find_many(self, query: dict):
        try:
            return list(self.collection.find(query))
        except PyMongoError as e:
            logger.error(f"find_many error: {e}")
            raise

    # Tek belge ekle
    def insert_one(self, doc: dict):
        try:
            result = self.collection.insert_one(doc)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return result
        except PyMongoError as e:
            logger.error(f"insert_one error: {e}")
            raise

    # Tek belge güncelle
    def update_one(self, query: dict, update: dict):
        try:
            result = self.collection.update_one(query, update)
            logger.info(f"Matched {result.matched_count} documents, Modified {result.modified_count}")
            return result
        except PyMongoError as e:
            logger.error(f"update_one error: {e}")
            raise

    # Tek belge bul ve güncelle, atomik
    def find_one_and_update(self, query: dict, update: dict, return_document=ReturnDocument.AFTER):
        try:
            doc = self.collection.find_one_and_update(query, update, return_document=return_document)
            if doc:
                logger.info(f"Document updated: {doc}")
            else:
                logger.info("No document matched the query for update")
            return doc
        except PyMongoError as e:
            logger.error(f"find_one_and_update error: {e}")
            raise
