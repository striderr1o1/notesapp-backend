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
        self.notebooks_coll = self.database["notebooks"]
        self.notes_coll = self.database["notes"]
        
        return
    
    def create_notebook(self, username, notebookname):
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
        return str(notebookid)
  
    def get_notebook(self, nbID):
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
        storing_status = self.store_noteid_in_notebook(str(note_id), notebook_id)
        if not storing_status:
            return False
        return True

    def store_noteid_in_notebook(self, note_id, notebook_id):
        updated_object = self.notebooks_coll.update_one({
            "_id": ObjectId(notebook_id)
            },
             {
                "$addToSet":{
                     "notes": note_id
                    }
                 }
            )
        if not updated_object:
            return False
        return True

    #working but need to add some error handling plus next
    # i need to create get nodes and update notes

    def get_note_from_id(self, noteid):
        objectid = ObjectId(noteid)
        note  = self.notes_coll.find_one({"_id":objectid })
        if not note:
            raise HTTPException(status = 400, detail="failed to create note")
        note["_id"] = str(note["_id"])
        return note

    #returning note but next need to integrate it with frontend

    def replace_note_by_id(self, noteid, note_contents):
        objectid = ObjectId(noteid)
        query = {"_id": objectid}
        update = { "$set" : { "data": note_contents}}
        note  = self.notes_coll.update_one(query, update)
        if not note:
            raise HTTPException(status = 400, detail="failed to update note")
        return True

    def delete_note(self, noteid, notebook_id):
        #delete note from notes collection, return notebook id 
        #and delete it from that notebook as well
        resp = self._delete_note_in_collection(noteid)
        resp2 = self._delete_note_in_notebook(noteid, notebook_id)
        return resp2

    def _delete_note_in_collection(self, noteid):
        objectid = ObjectId(noteid)
        query = {"_id": objectid}
        resp  = self.notes_coll.delete_one(query)       
        print(resp)
        return resp 

    def _delete_note_in_notebook(self, noteid, notebookid):
        notebook = self.get_notebook(notebookid)
        if not notebook:
            raise HTTPException(status = 400, detail="failed, no notebook with such name exists ")
        notes = notebook.get("notes", [])
        if noteid in notes:
            # if nid != noteid extract it to new list
            notes = [nid for nid in notes if nid != noteid]
        updated_object = self.notebooks_coll.update_one(
            {"_id": ObjectId(notebookid)},
            {"$set": {"notes": notes}}
        )
        if not updated_object:
            raise HTTPException(status = 400, detail="failed to update note ")
        return True

