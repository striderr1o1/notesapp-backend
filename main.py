from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from routes import auth_routes

load_dotenv()

app = FastAPI()

app.include_router(auth_routes.router)

    
