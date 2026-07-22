from app.llm.llm_service import LLMService

llm = LLMService()

response = llm.generate_response(
    "Say hello in one sentence."
)

print(response)