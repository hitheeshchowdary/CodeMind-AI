from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

import chromadb
from ollama import Client


from app.api.parser_api import (
    router as parser_router,
)

from app.api.upload_api import (
    router as upload_router,
)

from app.api.chat_api import (
    router as chat_router,
)

from app.api.project_api import (
    router as project_router,
)


app = FastAPI(
    title="RepoMind AI",
    description=(
        "AI-powered repository analysis "
        "and code assistant."
    ),
    version="1.0.0",
)


# =========================================
# CORS
# =========================================

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


# =========================================
# API ROUTERS
# =========================================

app.include_router(
    parser_router,
)

app.include_router(
    upload_router,
)

app.include_router(
    chat_router,
)

app.include_router(
    project_router,
)


# =========================================
# HOME
# =========================================

@app.get("/")
def home():
    return {
        "message": (
            "Welcome to RepoMind AI 🚀"
        ),
    }


# =========================================
# HEALTH CHECK
# =========================================

@app.get("/health")
def health_check():
    """
    Check the health of RepoMind AI services.

    Checks:
    - ChromaDB
    - Ollama
    """

    health = {
        "status": "healthy",
        "chromadb": "disconnected",
        "ollama": "disconnected",
    }

    # -------------------------------------
    # ChromaDB
    # -------------------------------------

    try:
        client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        client.get_or_create_collection(
            name="repository_chunks"
        )

        health["chromadb"] = "connected"

    except Exception:
        health["status"] = "unhealthy"

    # -------------------------------------
    # Ollama
    # -------------------------------------

    try:
        ollama_client = Client(
            host="http://localhost:11434"
        )

        ollama_client.list()

        health["ollama"] = "connected"

    except Exception:
        health["status"] = "unhealthy"

    return health