from app.vectorstore import ChromaService

db = ChromaService()

results = db.search_chunks(
    repository_name="my-repository",
    query="How is the upload API implemented?",
    top_k=3
)

print("\nSearch Results:\n")
print(results)