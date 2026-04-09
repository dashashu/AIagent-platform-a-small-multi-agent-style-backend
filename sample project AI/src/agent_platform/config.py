from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", env_file=".env", extra="ignore")

    # Optional: plug in your trained / hosted model (OpenAI-compatible API)
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "your-trained-model"
    use_llm_routing: bool = False

    # Cassandra (optional; DB agent degrades gracefully if unset)
    cassandra_hosts: str = ""  # comma-separated
    cassandra_keyspace: str = ""
    cassandra_username: str = ""
    cassandra_password: str = ""

    # Ticketing REST backend (optional; MCP can call these)
    ticketing_base_url: str = ""
    ticketing_api_key: str = ""


settings = Settings()
