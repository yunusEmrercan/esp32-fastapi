# mongo.py
from pymongo import MongoClient
import logging

class MongoDB:
    def __init__(self, db_name, collection_name, uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_document(self, data: dict):
        try:
            self.collection.insert_one(data)
        except Exception as e:
            logging.error(f"MongoDB insert error: {e}")
            raise

    def update_document(self, filter_query: dict, update_data: dict, upsert=False):
        try:
            self.collection.update_one(filter_query, {"$set": update_data}, upsert=upsert)
        except Exception as e:
            logging.error(f"MongoDB update error: {e}")
            raise

    def find_document(self, filter_query: dict):
        try:
            return self.collection.find_one(filter_query)
        except Exception as e:
            logging.error(f"MongoDB find error: {e}")
            raise

    def find_documents(self, filter_query: dict={}):
        try:
            return list(self.collection.find(filter_query))
        except Exception as e:
            logging.error(f"MongoDB find all error: {e}")
            raise
