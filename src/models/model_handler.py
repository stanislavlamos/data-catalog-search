from src.models.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider


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
    def get_model(provider_name: str, model_name: str | None = None) -> OpenAIEmbeddingProvider: #| AnthropicEmbeddingProvider:
        if provider_name == "anthropic":
            raise ValueError(f"Unsupported provider: {provider_name}")#return AnthropicEmbeddingProvider(model_name)
        elif provider_name == "openai":
            return OpenAIEmbeddingProvider(model_name="text-embedding-3-large", dimensions=1536)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")