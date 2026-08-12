from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for generating text embeddings.

    The embedding model is loaded only once and reused
    by all EmbeddingService instances.
    """

    _model = None

    def __init__(self):
        if EmbeddingService._model is None:
            print("Loading embedding model...")

            EmbeddingService._model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

            print("Embedding model loaded successfully.")

        self.model = EmbeddingService._model

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate an embedding for empty text."
            )

        embedding = self.model.encode(text)

        return embedding.tolist()