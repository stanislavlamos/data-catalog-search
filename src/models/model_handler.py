from src.models.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider
from src.models.google_provider import GoogleEmbeddingProvider


class LLMProviderHandler:
    @staticmethod
    def get_model(provider_name: str, model_name: str) -> OpenAILLMProvider: #| AnthropicLLMProvider:
        if provider_name == "anthropic":
            raise ValueError(f"Unsupported provider: {provider_name}")
            #return AnthropicLLMProvider(model_name)
        elif provider_name == "openai":
            return OpenAILLMProvider(model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")


class EmbeddingProviderHandler:
    @staticmethod
    def get_model(provider_name: str, model_name: str | None = None) -> OpenAIEmbeddingProvider | GoogleEmbeddingProvider:
        return GoogleEmbeddingProvider(model_name="gemini-embedding-001", output_dimensionality=None)
        """
        if provider_name == "openai":
            return OpenAIEmbeddingProvider(model_name="text-embedding-3-large", dimensions=None)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
        """