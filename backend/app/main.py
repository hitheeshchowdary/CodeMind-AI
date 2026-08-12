from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from ollama import Client


from app.api.parser_api import router as parser_router
from app.api.upload_api import router as upload_router
from app.api.chat_api import router as chat_router


app = FastAPI(
    title="CodeMind AI",
    description="AI-powered repository analysis and code assistant.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
# Allows the React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(parser_router)
app.include_router(upload_router)
app.include_router(chat_router)


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to CodeMind AI 🚀"
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    """
    Check the health of CodeMind AI services.

    Checks:
    - ChromaDB
    - Ollama
    """

    health = {
        "status": "healthy",
        "chromadb": "disconnected",
        "ollama": "disconnected",
    }

    # -----------------------------
    # Check ChromaDB
    # -----------------------------
    try:
        client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Access the collection to verify
        # that ChromaDB is available.
        client.get_or_create_collection(
            name="repository_chunks"
        )

        health["chromadb"] = "connected"

    except Exception:
        health["status"] = "unhealthy"


    # -----------------------------
    # Check Ollama
    # -----------------------------
    try:
        ollama_client = Client(
            host="http://localhost:11434"
        )

        ollama_client.list()

        health["ollama"] = "connected"

    except Exception:
        health["status"] = "unhealthy"


    return health