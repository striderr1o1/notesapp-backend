from bson.objectid import ObjectId
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from fastapi import HTTPException
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
         "created_at": datetime.utcnow(), 
         "notes": []

            })
        #create notebook
        #create notebook id
        #return id to async endpoint function
        #store id in user auth data
        notebookid = result.inserted_id 
        return notebookid 
  
    def get_notebook(self, nbID):
        self.notebooks_coll = self.database["notebooks"]
        objectid = ObjectId(nbID)
        nbData = self.notebooks_coll.find_one({"_id":objectid })
        return nbData

    def get_notebook_data(self, nbID):
        nbData = self.get_notebook(nbID)
        if not nbData:
            return None 
        nbData["_id"] = str(nbData["_id"])
        return nbData

    def create_note(self, note_name, data, username, notebook_id):
        self.notes_coll = self.database["notes"]
        result = self.notes_coll.insert_one({
        "notename": note_name,
        "username": username,
        "notebook_id": notebook_id,
        "data": data
           })
        note_id = result.inserted_id
        if not note_id:
            raise HTTPException(status = 400, detail="failed to create note")
            return False
        self.store_noteid_in_notebook(note_id, notebook_id)
        return True

    def store_noteid_in_notebook(self, note_id, notebook_id):
        self.notebooks_coll = self.database["notebooks"]
        self.notebooks_coll.update_one({
            "_id": ObjectId(notebook_id)
            },
             {
                "$addToSet":{
                     "notes": note_id
                    }
                 }
            )
        return True

    #working but need to add some error handling plus next
    # i need to create get nodes and update notes
