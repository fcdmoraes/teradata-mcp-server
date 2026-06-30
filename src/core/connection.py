"""
Gerenciamento de conexão com o Teradata via SQLAlchemy.
"""

import logging
from urllib.parse import parse_qs, urlencode, urlparse

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from core.config import settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None


def get_engine() -> Engine:
    """Retorna a engine singleton, criando-a na primeira chamada."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def _build_engine() -> Engine:
    """Cria um SQLAlchemy engine a partir das configurações."""
    if not settings.database_uri:
        raise ValueError("DATABASE_URI não configurado. Defina no .env ou variável de ambiente.")

    parsed = urlparse(settings.database_uri)
    uri_params = parse_qs(parsed.query, keep_blank_values=True)

    # LOGMECH das configurações tem precedência sobre o da URI
    uri_params.pop("LOGMECH", None)
    uri_params["LOGMECH"] = [settings.logmech]

    query_string = urlencode({k: v[0] for k, v in uri_params.items()})
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 1025
    db = parsed.path.lstrip("/")

    url = f"teradatasql://{user}:{password}@{host}:{port}/{db}?{query_string}"

    engine = create_engine(
        url,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout,
        pool_pre_ping=True,
    )
    logger.info(f"SQLAlchemy engine criado para {host}:{port}/{db}")
    return engine
