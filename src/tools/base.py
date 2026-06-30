"""
Tools base do Teradata MCP Server.

Ferramentas fundamentais: teste de conexão e consultas SQL.
"""

import json
import logging

from sqlalchemy import text

from core.config import settings
from core.connection import get_engine

logger = logging.getLogger(__name__)


def ping() -> str:
    """
    Testa a conexão com o servidor Teradata.

    Executa um SELECT simples e retorna a versão do banco,
    confirmando que a conexão está ativa e configurada corretamente.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT InfoData FROM DBC.DBCInfo WHERE InfoKey = 'VERSION'"))
            row = result.fetchone()
            version = row[0] if row else "desconhecida"
        return f"Conexão OK — Teradata versão {version}"
    except ValueError as e:
        return f"Erro de configuração: {e}"
    except Exception as e:
        return f"Falha na conexão: {e}"


def read_query(sql: str, row_limit: int = 0) -> str:
    """
    Executa uma consulta SQL no Teradata e retorna os resultados.

    Args:
        sql: Instrução SQL a executar (SELECT recomendado).
        row_limit: Número máximo de linhas. 0 usa o padrão configurado (DEFAULT_ROW_LIMIT).
                   Não pode exceder MAX_ROW_LIMIT.

    Returns:
        Resultados em formato JSON (lista de objetos) ou mensagem de erro.
    """
    effective_limit = row_limit if row_limit > 0 else settings.default_row_limit
    effective_limit = min(effective_limit, settings.max_row_limit)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = result.fetchmany(effective_limit)

        data = [dict(zip(columns, row)) for row in rows]
        response = {"row_count": len(data), "truncated": len(data) == effective_limit, "rows": data}
        return json.dumps(response, default=str, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": f"Erro de configuração: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def list_tables(database: str) -> str:
    """
    Lista as tabelas e views de um banco de dados Teradata.

    Args:
        database: Nome do database (schema) a consultar.

    Returns:
        JSON com nome, tipo e data de criação de cada objeto.
    """
    sql = """
        SELECT TableName, TableKind, CreateTimeStamp
        FROM DBC.TablesV
        WHERE DatabaseName = :db
          AND TableKind IN ('T', 'V', 'O')
        ORDER BY TableKind, TableName
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql), {"db": database})
            columns = list(result.keys())
            rows = result.fetchall()

        kind_map = {"T": "Table", "V": "View", "O": "Table (NoPI)"}
        data = [
            {
                "name": row[0].strip(),
                "type": kind_map.get(row[1], row[1]),
                "created_at": str(row[2]),
            }
            for row in rows
        ]
        return json.dumps({"database": database, "object_count": len(data), "objects": data}, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": f"Erro de configuração: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def table_preview(database: str, table: str, row_limit: int = 10) -> str:
    """
    Retorna uma amostra das primeiras linhas de uma tabela.

    Args:
        database: Nome do database onde a tabela está.
        table: Nome da tabela.
        row_limit: Número de linhas a retornar (padrão 10, máximo MAX_ROW_LIMIT).

    Returns:
        JSON com colunas e linhas da amostra.
    """
    effective_limit = min(row_limit, settings.max_row_limit)
    sql = f"SELECT TOP {effective_limit} * FROM {database}.{table}"

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = result.fetchall()

        data = [dict(zip(columns, row)) for row in rows]
        return json.dumps(
            {"database": database, "table": table, "row_count": len(data), "rows": data},
            default=str,
            ensure_ascii=False,
        )
    except ValueError as e:
        return json.dumps({"error": f"Erro de configuração: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
