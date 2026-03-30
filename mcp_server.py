#!/usr/bin/env python3
"""MCP server exposing DuckDB Iceberg queries to Claude Desktop.

Setup:
    pip install mcp duckdb
    Then add to Claude Desktop config — see README.md for instructions.
"""

import asyncio
import os

import duckdb
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# ---------------------------------------------------------------------------
# Credentials & DuckDB setup
# ---------------------------------------------------------------------------

def load_env(path: str | None = None) -> None:
    env_path = path or os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip().strip("'\"")


def setup_duckdb() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect()
    conn.execute("INSTALL iceberg; LOAD iceberg;")
    conn.execute(f"""
        CREATE SECRET iceberg_secret (
            TYPE iceberg,
            CLIENT_ID     '{os.environ["ICEBERG_CLIENT_ID"]}',
            CLIENT_SECRET '{os.environ["ICEBERG_CLIENT_SECRET"]}',
            SCOPE         '{os.environ["ICEBERG_SCOPE"]}',
            ENDPOINT      '{os.environ["ICEBERG_ENDPOINT"]}'
        );
    """)
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute(f"SET s3_access_key_id     = '{os.environ['AWS_ACCESS_KEY_ID']}';")
    conn.execute(f"SET s3_secret_access_key = '{os.environ['AWS_SECRET_ACCESS_KEY']}';")
    conn.execute(f"SET s3_session_token     = '{os.environ['AWS_SESSION_TOKEN']}';")
    conn.execute(f"SET s3_region            = '{os.environ['AWS_REGION']}';")
    conn.execute("SET s3_url_style = 'vhost';")
    conn.execute("SET http_keep_alive = false;")
    conn.execute(
        f"ATTACH '{os.environ['ICEBERG_CATALOG_NAME']}' AS iceberg_catalog "
        "(TYPE iceberg, SECRET iceberg_secret);"
    )
    return conn


def _format_result(result) -> str:
    rows = result.fetchall()
    columns = [desc[0] for desc in result.description]
    if not rows:
        return "Query returned no results."
    lines = [" | ".join(columns)]
    lines.append("-" * len(lines[0]))
    for row in rows[:200]:
        lines.append(" | ".join(str(v) for v in row))
    if len(rows) > 200:
        lines.append(f"... ({len(rows) - 200} more rows truncated)")
    return "\n".join(lines)


def run_query(query: str) -> str:
    global conn
    try:
        return _format_result(conn.execute(query))
    except Exception:
        # Credentials may have expired — reload .env and reconnect, then retry once.
        try:
            load_env()
            conn = setup_duckdb()
            return _format_result(conn.execute(query))
        except Exception as e:
            return f"Error: {e}"


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

load_env()
conn = setup_duckdb()

server = Server("duckdb-iceberg")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="run_sql_query",
            description=(
                "Execute a SQL query against DuckDB with the Polaris Iceberg catalog. "
                "The catalog is named 'iceberg_catalog'. "
                "List schemas:  SELECT schema_name FROM information_schema.schemata WHERE catalog_name = 'iceberg_catalog'; "
                "List tables:   SHOW TABLES FROM iceberg_catalog.<schema_name>; "
                "Query a table: SELECT * FROM iceberg_catalog.<schema>.<table> LIMIT 10;"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute.",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "run_sql_query":
        result = run_query(arguments["query"])
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
