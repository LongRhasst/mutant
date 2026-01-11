from fastapi import FastAPI
from App.Router import router

app = FastAPI()
app.include_router(router)