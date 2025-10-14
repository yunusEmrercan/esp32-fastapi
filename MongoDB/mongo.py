from pymongo import MongoClient



class MongoDB:
    def __init__(self, db, collection, connection_url='mongodb://localhost:27017/'):
        self.client = MongoClient(connection_url)
        self.db = self.client[db]
        self.collection = self.db[collection]
        print(self.client.list_database_names())
        print(self.db.list_collection_names())


    def find_document(self, query):
        result = self.collection.find_one(query)
        return result

    def close_connection(self):
        self.client.close()

