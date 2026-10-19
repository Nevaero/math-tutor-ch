from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEO_", extra="ignore")

    # API IA Infomaniak (compatible OpenAI)
    infomaniak_api_token: str = ""
    infomaniak_product_id: str = ""
    infomaniak_base_url: str = "https://api.infomaniak.com/2/ai/{product_id}/openai/v1"
    chat_model: str = "Qwen/Qwen3.5-122B-A10B-FP8"
    vision_model: str = ""  # à choisir dans le catalogue (python -m leo.models)
    embedding_model: str = ""  # idem ; vide = recherche PER en BM25 seul

    # Prix en CHF par million de tokens, pour l'estimation de coût (à renseigner)
    price_in_per_mtok: float = 0.0
    price_out_per_mtok: float = 0.0

    sandbox_timeout_s: float = 15.0
    session_ttl_s: int = 2 * 3600
    max_hint_level: int = 3

    @property
    def base_url(self) -> str:
        return self.infomaniak_base_url.format(product_id=self.infomaniak_product_id)


settings = Settings()
