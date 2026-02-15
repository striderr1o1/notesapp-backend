from fastapi import HTTPException, Response, APIRouter, Depends, status
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector
from database.mongo_db import mongo_db_connector
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)
mongo_db_conn = mongo_db_connector()

class Note_object(BaseModel):
    note_contents: dict
    note_id: str

class NoteDataFromUser(BaseModel):
    note_id: str

class Notebook(BaseModel):
    notebookname: str

class Note(BaseModel):
    notebook_id: str
    notename: str
    data: str
class NotebookData(BaseModel):
    notebook_id: str

class NoteID(BaseModel):
    note_id: str
    notebook_id: str

@router.get("/getnotebooks")
async def get_notebooks(user=Depends(auth_obj.validate_session)):
    #process 
    username = user["username"]
    #get notebook names from user data
    userdata = auth_obj.get_user_data(username)
    print(userdata)
    notebooks_list = [] 
    if not "notebook_ids" in userdata:
       # raise HTTPException(status=404, detail="Not found")
        return {"notebooks_list": notebooks_list,
            "username": username} 

    notebooksIDlist= userdata["notebook_ids"]
    for nbID in notebooksIDlist:
        nbdata = mongo_db_conn.get_notebook_data(str(nbID))
        if nbdata == None:
            print("NONE")
            
        notebooks_list.append(nbdata)
    print(notebooks_list)
    return {"notebooks_list": notebooks_list,
            "username": username} 

@router.post("/createnotebook")
async def create_Notebook(notebookdata: Notebook, user=Depends(auth_obj.validate_session)):
    notebook_id =  mongo_db_conn.create_notebook(user["username"],notebookdata.notebookname)
  #insert id in userdata
    enter_id_status = auth_obj.enterID_in_userdata(user["username"],notebook_id)
    if enter_id_status == False:
        raise HTTPException(status_code=409, detail="failed to insert notebook")
    return JSONResponse(content={"notebookid": str(notebook_id),
                                 "message": "notebook created successfully"
        }, status_code =201) 


@router.post("/createnote")
async def create_note( notedata: Note, user=Depends(auth_obj.validate_session)):
    status =  mongo_db_conn.create_note(notedata.notename, notedata.data, user["username"], notedata.notebook_id)        
    if status == False:
       raise HTTPException(status=400, detail="Failed")
    return True

@router.post("/getnotes")
async def get_notes(notebook_data: NotebookData, user=Depends(auth_obj.validate_session)):
    notebook_data = mongo_db_conn.get_notebook_data(notebook_data.notebook_id)
    print(notebook_data)
    if not notebook_data:
        raise HTTPException(status_code=404, detail="failed to fetch notes")

    return notebook_data["notes"]


@router.post("/getnotefromid")
async def get_note_frm_id(NoteData: NoteDataFromUser, user=Depends(auth_obj.validate_session) ):
   note =  mongo_db_conn.get_note_from_id(NoteData.note_id)
   return note 

@router.put("/replacenote")
async def Replace_Note(nt_obj: Note_object, user=Depends(auth_obj.validate_session)):
    status = mongo_db_conn.replace_note_by_id(nt_obj.note_id, nt_obj.note_contents)
    return status



@router.post("/deletenote")
async def Delete_note(note_id_object: NoteID, user=Depends(auth_obj.validate_session)):
    resp = mongo_db_conn.delete_note(note_id_object.note_id, note_id_object.notebook_id)
    return resp

@router.post("/deletenotebook")
async def Delete_notebook(Notebook_data: NotebookData, user=Depends(auth_obj.validate_session)):
    notebook_id = Notebook_data.notebook_id
    resp = mongo_db_conn.delete_notebook_and_notes(notebook_id)
    resp2 = auth_obj.delete_notebook_from_user(user["username"], notebook_id)
    return ""
