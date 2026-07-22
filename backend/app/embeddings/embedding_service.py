from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for generating text embeddings.
    """

    def __init__(self):
        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded successfully.")

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for the given text.
        """

        embedding = self.model.encode(text)

        return embedding.tolist()