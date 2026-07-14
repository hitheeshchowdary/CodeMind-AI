from fastapi import FastAPI

from app.api.parser_api import router as parser_router
from app.api.upload_api import router as upload_router

app = FastAPI(title="CodeMind AI")

app.include_router(parser_router)
app.include_router(upload_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CodeMind AI 🚀"
    }