from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from auth.auth import Authentication
from database.authorizationDB import mongo_db_auth_connector

load_dotenv()

app = FastAPI()
auth_dbconnector = mongo_db_auth_connector()
auth_obj = Authentication(auth_dbconnector)

@app.post("/signup")
async def signup(username: str, password: str, email: str):
        status = auth_obj.sign_up(username, password, email)
        if status["Exception"] is not None:
            raise HTTPException(status_code=401, detail=f"Account Not Registered.")
        return status
