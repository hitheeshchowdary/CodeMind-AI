from app.embeddings.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

embedding = embedding_service.generate_embedding(
    "def upload_repository(file):"
)

print(len(embedding))

print(embedding[:10])