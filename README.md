# Teradata MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server for Teradata. Enables Claude (via Cowork or Claude Desktop) to run SQL queries, explore metadata, and interact directly with Teradata databases.

---

## Features

- Execute arbitrary SQL queries with configurable row limits
- List tables and views within a database
- Preview sample rows from any table
- Test connectivity and retrieve the database version
- Environment-based configuration via `.env`
- Supports `stdio` transport (Claude Desktop / Cowork) and `streamable-http`

---

## Tools

| Tool | Description |
|---|---|
| `ping` | Tests the connection and returns the Teradata version |
| `read_query` | Executes a SQL statement and returns results as JSON |
| `list_tables` | Lists tables and views in a given database |
| `table_preview` | Returns a sample of the first rows from a table |

### Details

**`ping()`**
Confirms the connection is active. Useful for validating configuration before running queries.

**`read_query(sql, row_limit?)`**
Executes any SQL statement. `row_limit` is optional — defaults to `DEFAULT_ROW_LIMIT` (1000). Never exceeds `MAX_ROW_LIMIT` (50000). Returns `truncated: true` when results were cut off.

**`list_tables(database)`**
Queries `DBC.TablesV` and returns the name, type (Table / View), and creation date of each object in the given database.

**`table_preview(database, table, row_limit?)`**
Executes `SELECT TOP N * FROM database.table`. Default `row_limit` is 10.

---

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Access to a Teradata server

### Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd teradata-mcp-server

# 2. Install dependencies
uv sync

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your Teradata credentials

# 4. Test the connection
uv run teradata-mcp-server
```

---

## Configuration

### Environment variables (`.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URI` | ✅ | — | Connection URI: `teradata://user:password@host:1025/database` |
| `LOGMECH` | — | `TD2` | Authentication mechanism (`TD2` or `LDAP`) |
| `MCP_TRANSPORT` | — | `stdio` | MCP transport (`stdio` or `streamable-http`) |
| `MCP_HOST` | — | `localhost` | Host for HTTP transport |
| `MCP_PORT` | — | `8001` | Port for HTTP transport |
| `TD_POOL_SIZE` | — | `5` | Connection pool size |
| `TD_MAX_OVERFLOW` | — | `10` | Extra connections allowed above pool size |
| `TD_POOL_TIMEOUT` | — | `30` | Timeout to acquire a connection (seconds) |
| `DEFAULT_ROW_LIMIT` | — | `1000` | Default row limit for `read_query` |
| `MAX_ROW_LIMIT` | — | `50000` | Hard ceiling — callers cannot exceed this |
| `LOGGING_LEVEL` | — | `WARNING` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Cowork Configuration

In Claude Cowork (or Claude Desktop), go to **Settings → Claude Cowork → Edit Config** and add the block below inside `mcpServers`:

```json
{
  "mcpServers": {
    "teradata": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/teradata-mcp-server",
        "run",
        "teradata-mcp-server"
      ],
      "env": {
        "DATABASE_URI": "teradata://user:password@host:1025/database"
      }
    }
  }
}
```

> Replace `/path/to/teradata-mcp-server` with the absolute path to the project on your machine and fill in your credentials in `DATABASE_URI`.

If you prefer to keep credentials in `.env` rather than exposing them in the config JSON, omit the `"env"` field — the server reads `.env` automatically on startup.

---

## Project Structure

```
teradata-mcp-server/
├── .env.example                  # Environment variables template
├── pyproject.toml                # Dependencies and entry point (uv/hatchling)
├── README.md
└── src/
    ├── core/
    │   ├── __init__.py
    │   ├── config.py             # Settings (pydantic-settings, reads .env)
    │   └── connection.py         # SQLAlchemy singleton engine (get_engine)
    ├── tools/
    │   ├── __init__.py
    │   └── base.py               # Tools: ping, read_query, list_tables, table_preview
    └── server/
        ├── __init__.py
        └── teradata_mcp_server.py  # Entry point: FastMCP instance + mcp.run()
```
