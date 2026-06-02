from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/careergraph"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    llm_provider: str = ""
    llm_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"


settings = Settings()
