from fastapi import HTTPException, Response, APIRouter, Depends
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector


router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)

@router.post("/sendmessage")
async def get_notes( message: str, user=Depends(auth_obj.validate_session)):
    
    return {"username": user["username"],
            "email": user["email"],
            "note": message}
    


