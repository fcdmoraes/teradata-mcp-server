from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Conexão com o Teradata ---
    # URI no formato: teradata://usuario:senha@host:1025/database
    database_uri: str | None = None

    # Mecanismo de autenticação (TD2 = usuário/senha padrão do Teradata)
    logmech: str = "TD2"

    # --- Pool de conexões SQLAlchemy ---
    pool_size: int = 5         # Conexões mantidas abertas
    max_overflow: int = 10     # Conexões extras permitidas acima do pool_size
    pool_timeout: int = 30     # Segundos para aguardar uma conexão disponível

    # --- Transporte MCP ---
    # "stdio" para Claude Desktop/CLI; "streamable-http" para HTTP
    mcp_transport: str = "stdio"
    mcp_host: str = "localhost"
    mcp_port: int = 8001
    mcp_path: str = "/mcp/"

    # --- Limites de resultado ---
    default_row_limit: int = 1000   # Linhas retornadas por padrão em consultas SQL
    max_row_limit: int = 50000      # Teto máximo permitido

    # --- Logging ---
    logging_level: str = "WARNING"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
