from ollama import Client


class LLMService:
    """
    Handles communication with the local Ollama server.
    """

    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "mistral:latest"

    def generate_response(self, prompt: str) -> str:
        """
        Sends the prompt to Ollama and returns the generated response.
        """

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CodeMind AI, an expert software engineer. "
                            "Answer questions ONLY using the repository context provided. "
                            "If the answer is not present, say "
                            "'I couldn't find that information in the repository.'"
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            return response["message"]["content"].strip()

        except Exception as e:
            raise RuntimeError(f"Ollama Error: {e}")