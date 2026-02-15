import os
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
class mongo_db_auth_connector:
    def __init__(self):
        self.username = os.environ.get("MONGO_USERNAME")
        self.password = os.environ.get("MONGO_PASSWORD")
        self.uri = f"mongodb+srv://{self.username}:{self.password}@cluster0.tiufhor.mongodb.net/?appName=Cluster0"
        self.client = None
        self.database = None
        self.collection = None
        self._connect()
        return

    def _connect(self):
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.database = self.client["auth"]
        self.collection = self.database["username_passwords"]
        return

    def insert_user(self, username, password, email):
        user = {
            "username": username,
            "password": password,
            "email": email
        }
        searching_user = self.find_user(username)
        if searching_user:
            return {
                    "Exception" : "user exists" 
            }
        try: 
            self.collection.insert_one(user)
            return {
                "status": "User created",
                "Exception": None
            }
        except Exception as e:
            return {
                "Exception" : e
            }
    
    def find_user(self, username):
        user_data = self.collection.find_one({"username": username})
        return user_data

    def enter_id_in_userdata(self,username, ID):
        userdata = self.find_user(username)
        if not userdata:
            return False

        self.collection.update_one({
          "username": username
            },
            {
            "$addToSet": {
               "notebook_ids": ID
                }
            }
            )
        return True

    def update_collection(self, filter_criteria, update_oper):
        resp = self.collection.update_one(filter_criteria, update_oper)
        return resp

    
