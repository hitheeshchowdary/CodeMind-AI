# RepoMind AI

### AI-Powered Repository Understanding Assistant

RepoMind AI is an AI-powered application that helps developers understand software repositories using natural-language questions.

Instead of manually searching through files, users can upload a repository and ask questions about its:

- Project purpose
- Architecture
- Technologies
- Files
- Functions
- Classes
- Implementation logic
- Code workflow

RepoMind AI analyzes the repository, creates searchable code representations, retrieves relevant code, and uses a local LLM to generate repository-aware answers.

---

## ✨ Features

- 📦 Upload repository as a ZIP file
- 🔍 Automatically scan repository files
- 🐍 Python AST-based code analysis
- 📊 Repository analytics
- ✂️ Code chunking
- 🧠 Semantic embeddings
- 🔎 Semantic code search
- 🗄️ ChromaDB vector database
- 🤖 Retrieval-Augmented Generation (RAG)
- 💬 Natural-language code questions
- 📚 Repository-aware answers
- 🧭 Intelligent question classification
- 💡 Context-aware follow-up questions
- 🖥️ React frontend
- ⚡ FastAPI backend
- 🔐 Local LLM inference using Ollama

---

## 🛠️ Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn

### AI / ML

- Sentence Transformers
- Python AST
- Retrieval-Augmented Generation (RAG)
- Ollama
- Llama 3.2 3B

### Database

- ChromaDB

### Development

- Git
- GitHub
- VS Code

---

## 🏗️ How It Works

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ├── Repository Upload
 │
 ├── Repository Parsing
 │
 ├── Python AST Analysis
 │
 ├── Repository Analytics
 │
 ├── Code Chunking
 │
 └── Embedding Generation
          │
          ▼
      ChromaDB
          │
          ▼
   User Question
          │
          ▼
 Question Classification
          │
          ▼
 Semantic Retrieval
          │
          ▼
 Relevant Code
          │
          ▼
 Prompt Builder
          │
          ▼
 Ollama / Llama 3.2
          │
          ▼
      AI Answer

🚀 Getting Started
This section explains how to run RepoMind AI from a fresh clone.
1. Clone the Repository
Open PowerShell, Command Prompt, or Terminal and run:
git clone https://github.com/hitheeshchowdary/RepoMind-AI.git

Move into the project:
cd RepoMind-AI

2. Backend Setup
Open a terminal in the project root and move into the backend:
cd backend

Create a Python virtual environment
python -m venv .venv

Activate the virtual environment
Windows PowerShell
.venv\Scripts\Activate.ps1

Windows Command Prompt
.venv\Scripts\activate

Install backend dependencies
pip install -r requirements.txt

3. Install and Setup Ollama
RepoMind AI currently uses Ollama for local LLM inference.
Install Ollama on your system and download the required model:
ollama pull llama3.2:3b

Verify that the model is available:
ollama list

You should see:
llama3.2:3b

Make sure Ollama is running before using RepoMind AI.
4. Start the Backend
Make sure you are inside:
RepoMind-AI/backend

Run:
uvicorn app.main:app

The FastAPI backend will start.
Keep this terminal running while using the application.
5. Start the Frontend
Open a new terminal.
Go back to the project root:
cd RepoMind-AI

Move into the frontend:
cd frontend

Install frontend dependencies:
npm install

Start the development server:
npm run dev

Vite will display a local URL similar to:
http://localhost:5173

Open that URL in your browser.
🧾 Complete Command List
If Python, Node.js, Git, and Ollama are already installed, the basic setup is:
Terminal 1 — Backend
git clone https://github.com/hitheeshchowdary/RepoMind-AI.git
cd RepoMind-AI
cd backend
python -m venv .venv

Activate the environment.
PowerShell
.venv\Scripts\Activate.ps1

Then:
pip install -r requirements.txt
uvicorn app.main:app

Terminal 2 — Ollama
Make sure Ollama is installed and download the model:
ollama pull llama3.2:3b

Keep Ollama running.
Terminal 3 — Frontend
cd RepoMind-AI
cd frontend
npm install
npm run dev

Then open the URL provided by Vite.
📂 Project Structure
RepoMind-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── embeddings/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── parser/
│   │   ├── services/
│   │   └── vectorstore/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md

💬 How to Use
1. Start the backend.
2. Start Ollama.
3. Start the frontend.
4. Open RepoMind AI in your browser.
5. Upload a repository ZIP file.
6. Wait for the repository to finish indexing.
7. Ask questions about the repository.
8. Use the suggested follow-up questions to explore the codebase further.
Example Questions
What does this project do?

Explain the project architecture.

What technologies are used?

What is the role of resume_parser.py?

How does the parsing process work?

Where is the main application logic implemented?

🔎 Repository Processing
When a repository is uploaded, RepoMind AI processes it through the following pipeline:
Repository ZIP
      ↓
Extraction
      ↓
Repository Scanning
      ↓
File Parsing
      ↓
Python AST Analysis
      ↓
Repository Analytics
      ↓
Code Chunking
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Ready for Questions

When a question is asked:
User Question
      ↓
Question Classification
      ↓
Query Construction
      ↓
Semantic Search
      ↓
Relevant Code Chunks
      ↓
Prompt Construction
      ↓
Ollama / Llama 3.2
      ↓
AI Answer

🧠 Why RAG?
A general-purpose LLM does not automatically know the contents of a user's uploaded repository.
RepoMind AI uses Retrieval-Augmented Generation (RAG) to provide relevant repository code to the LLM before generating an answer.
This allows the system to answer questions using evidence retrieved from the uploaded repository rather than relying only on the model's pretrained knowledge.
⚡ Performance
RepoMind AI separates repository retrieval from LLM generation.
During development, semantic retrieval using embeddings and ChromaDB is significantly faster than local LLM generation.
The current major response-latency component is local LLM inference.
Performance optimization is therefore an important part of the project's ongoing development.
🔬 Research Direction
The current version of RepoMind AI provides a RAG-based repository understanding system.
The next stage of the project is to introduce Agentic AI to make repository question answering more adaptive.
The planned architecture will include:
- Intelligent question routing
- Specialized repository agents
- Code search agents
- Architecture analysis
- Multi-step retrieval
- Evidence verification
- Adaptive reasoning
- Latency-aware execution
The research objective is to investigate whether dynamic agent routing and evidence verification can improve repository-level code understanding while maintaining low response latency.
🔮 Future Work
- Public GitHub repository URL support
- Agentic AI integration
- LangGraph-based orchestration
- Code-aware chunking
- Multi-file reasoning
- Dependency-aware retrieval
- Evidence verification
- Improved retrieval accuracy
- Faster LLM inference
- RAG vs Agentic RAG evaluation
- Repository question benchmark dataset
👨‍💻 Author
Hitheesh Chowdary
B.Tech Computer Science and Engineering
Artificial Intelligence & Machine Learning