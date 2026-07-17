from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from chat_routes import router as chat_router
from doctor_routes import router as doctor_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(chat_router)
app.include_router(doctor_router)