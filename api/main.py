# api/main.py
from fastapi import FastAPI
from api.routers import tasks, done

app = FastAPI()
app.include_router(tasks.router)
app.include_router(done.router)

