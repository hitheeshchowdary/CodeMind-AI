from fastapi import FastAPI
from app.api.parser_api import router as parser_router

app = FastAPI(title="CodeMind AI")

app.include_router(parser_router)


@app.get("/")
def home():
    return {"message": "Welcome to CodeMind AI 🚀"}