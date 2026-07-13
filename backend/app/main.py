from fastapi import FastAPI

app = FastAPI(title="CodeMind AI")

@app.get("/")
def home():
    return {
        "message": "Welcome to CodeMind AI 🚀"
    }