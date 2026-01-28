from fastapi import HTTPException, Response, APIRouter, Depends
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector
from pydantic import BaseModel

class SignUpData(BaseModel):
    username: str
    password: str
    email: str

class LoginData(BaseModel):
    username: str
    password: str

load_dotenv()

router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)

@router.post("/signup")
async def signup(data: SignUpData):
    status = auth_obj.sign_up(data.username, data.password, data.email)
    if status["Exception"] is not None:
        raise HTTPException(status_code=401, detail="Account Not Registered.")
    return status

@router.post("/login")
async def Login(data: LoginData, response: Response):
    resp = auth_obj.login(data.username, data.password)
    if resp["status"] == False:
        raise HTTPException(status_code=401, detail=f"Failed To Login.")

    session_id = resp["session_id"]
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    return {"status": "successful"}

@router.get("/logout")
async def Logout(status=Depends(auth_obj.logout)):
    if(status["status"] == True):
        return status 
    raise HTTPException(status_code=401, detail=f"Failed To logout.")
