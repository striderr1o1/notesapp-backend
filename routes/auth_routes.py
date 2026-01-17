from fastapi import HTTPException, Response, APIRouter
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector
from database.redis_db import redis_connector


load_dotenv()

router = APIRouter()

auth_dbconnector = mongo_db_auth_connector()
redis_dbconnector = redis_connector()
auth_obj = Authentication(auth_dbconnector, redis_dbconnector)

@router.post("/signup")
async def signup(username: str, password: str, email: str):
    status = auth_obj.sign_up(username, password, email)
    if status["Exception"] is not None:
        raise HTTPException(status_code=401, detail=f"Account Not Registered.")
    return status

@router.post("/login")
async def Login(username: str, password: str, response: Response):
    resp = auth_obj.login(username, password)
    if resp["status"] == False:
        raise HTTPException(status_code=401, detail=f"Failed To Login.")

    session_id = resp["session_id"]
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return {"status": "successful"}


