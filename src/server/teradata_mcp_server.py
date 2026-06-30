"""
Teradata MCP Server — ponto de entrada.

Instancia o servidor FastMCP, registra as tools e inicia o transporte configurado.
"""

import logging
import sys

from fastmcp import FastMCP

from core.config import settings
from tools import base

logging.basicConfig(
    level=getattr(logging, settings.logging_level.upper(), logging.WARNING),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

mcp = FastMCP("teradata-mcp-server")

mcp.tool()(base.ping)
mcp.tool()(base.read_query)
mcp.tool()(base.list_tables)
mcp.tool()(base.table_preview)


def main() -> None:
    mcp.run(transport=settings.mcp_transport)


if __name__ == "__main__":
    main()
