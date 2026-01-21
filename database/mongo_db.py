from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
class mongo_db_connector:
    def __init__(self):
        self.username = os.environ.get("MONGO_USERNAME")
        self.password = os.environ.get("MONGO_PASSWORD")
        self.uri = f"mongodb+srv://{self.username}:{self.password}@cluster0.tiufhor.mongodb.net/?appName=Cluster0"
        self.database = None
        self.notebooks_coll = None
        self.notes_coll = None
        self._connect()
        return

    def _connect(self):
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.database = self.client["app-data"]
        
        return
    
    def create_notebook(self, username, notebookname):
        self.notebooks_coll = self.database["notebooks"]
        result = self.notebooks_coll.insert_one({
         "username": username,
         "notebook_name": notebookname,
         "created_at": datetime.utcnow() 

            })
        #create notebook
        #create notebook id
        #return id to async endpoint function
        #store id in user auth data
        notebookid = result.inserted_id 
        return notebookid 

       
