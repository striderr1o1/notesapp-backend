from fastapi import HTTPException, Response, APIRouter, Depends, status
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector
from database.mongo_db import mongo_db_connector
from fastapi.responses import JSONResponse
from pydantic import BaseModel
router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)
mongo_db_conn = mongo_db_connector()

class Notebook(BaseModel):
    notebookname: str
class Note(BaseModel):
    notebook_id: str
    notename: str
    data: str
  
@router.get("/getnotebooks")
async def get_notebooks(user=Depends(auth_obj.validate_session)):
    #process 
    username = user["username"]
    #get notebook names from user data
    userdata = auth_obj.get_user_data(username)
    if not userdata["notebook_ids"]:
        raise HTTPException(status=404, detail="Not found")
    notebooksIDlist= userdata["notebook_ids"]
    notebooks_list = [] 
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
#receive notebook id
#create note, store note id in notebook's data
#store note data i.e note name, note id, data and notebook id in notes collection in mongo db
