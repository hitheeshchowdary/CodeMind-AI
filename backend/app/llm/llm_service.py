from ollama import Client


class LLMService:
    """
    Handles communication with the local Ollama server.
    """

    def __init__(self):

        self.client = Client(
            host="http://localhost:11434"
        )

        self.model = "llama3.2:3b"

    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """
        Send a prompt to Ollama and return
        the generated response.
        """

        try:

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": 0.2,
                    "num_predict": 400,
                },
            )

            return (
                response["message"]["content"]
                .strip()
            )

        except Exception as error:

            raise RuntimeError(
                f"Ollama Error: {error}"
            )