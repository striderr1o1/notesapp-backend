from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from routes import auth_routes, notes_routes
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.106:8080", "http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(notes_routes.router)
    
