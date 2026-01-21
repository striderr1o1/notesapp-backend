from fastapi import HTTPException, Response, APIRouter, Depends, status
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector
from database.mongo_db import mongo_db_connector
from fastapi.responses import JSONResponse

router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)
mongo_db_conn = mongo_db_connector()
#@router.post("/sendmessage")
#async def get_notes( message: str, user=Depends(auth_obj.validate_session)):
#    
#    return {"username": user["username"],
#            "email": user["email"],
#            "note": message}
    
@router.get("/getnotebooks")
async def get_notebooks(user=Depends(auth_obj.validate_session)):
    #process 
    username = user["username"]
    #if username not exist, create collection
    return {"status": "ok"}

@router.post("/createnotebook")
async def create_Notebook(notebookname: str, user=Depends(auth_obj.validate_session)):
    notebook_id =  mongo_db_conn.create_notebook(user["username"], notebookname)
  #insert id in userdata
    enter_id_status = auth_obj.enterID_in_userdata(user["username"],notebook_id)
    if enter_id_status == False:
        raise HTTPException(status_code=409, detail="failed to insert notebook")
    return JSONResponse(content={"notebookid": str(notebook_id),
                                 "message": "notebook created successfully"
        }, status_code =201) 
