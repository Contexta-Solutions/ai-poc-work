from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from chat_routes import router as chat_router
from doctor_routes import router as doctor_router
from auth import router as auth_router, require_pass

# Every route needs the demo pass except /health and /api/login (see auth.py).
app = FastAPI(dependencies=[Depends(require_pass)])

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
app.include_router(auth_router)