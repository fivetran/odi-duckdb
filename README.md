# DuckDB Iceberg & S3 Connector

Connect to a Fivetran Polaris Iceberg Catalog and AWS S3 via DuckDB. Supports two modes of use: an **interactive SQL shell** and a **Claude Desktop MCP integration** for natural language queries.

---

## Requirements

- **DuckDB**: [Install DuckDB](https://duckdb.org/docs/installation/)
- **Internet Access**: Required to download DuckDB extensions (`iceberg`, `httpfs`) and connect to the APIs.

---

## Setup

1. **Create a credentials file** — copy `.env_example` to `.env` and fill in your credentials:

```env
# Polaris Iceberg Credentials
ICEBERG_CLIENT_ID='XXX'
ICEBERG_CLIENT_SECRET='XXX'
ICEBERG_SCOPE='PRINCIPAL_ROLE:ALL'
ICEBERG_ENDPOINT='https://XXXXXXXXXXX.aws.polaris.fivetran.com/api/catalog'
ICEBERG_CATALOG_NAME='XXX'

# AWS S3 Credentials
AWS_ACCESS_KEY_ID='XXX'
AWS_SECRET_ACCESS_KEY='XXX'
AWS_SESSION_TOKEN='XXX'
AWS_REGION='us-west-2'
```

---

## Option 1 — Interactive DuckDB Shell

Launch a pre-configured DuckDB session with the Iceberg catalog already attached:

```bash
chmod +x run_script.sh
./run_script.sh
```

This will load credentials, initialize the DuckDB session, install and load the `iceberg` and `httpfs` extensions, configure S3, attach the catalog, and drop you into an interactive SQL shell.

**Example commands:**

```sql
-- List schemas
SELECT schema_name FROM information_schema.schemata WHERE catalog_name = 'iceberg_catalog';

-- List tables in a schema
SHOW TABLES FROM iceberg_catalog.mb_sql_10022026_agriculture;

-- Query a table
SELECT count(*) FROM iceberg_catalog.mb_sql_10022026_agriculture.california_wine_production;
```

---

## Option 2 — Claude Desktop MCP Integration

Query your Iceberg data in natural language directly from [Claude Desktop](https://claude.ai/download) using an MCP server.

### Setup

**1. Install Python dependencies** into the project virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install duckdb mcp pytz
```

**2. Configure Claude Desktop** — add the following to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "duckdb-iceberg": {
      "command": "/path/to/duckdbsqlscript/.venv/bin/python3",
      "args": ["/path/to/duckdbsqlscript/mcp_server.py"]
    }
  }
}
```

Replace `/path/to/duckdbsqlscript/` with the absolute path to this repository.

**3. Restart Claude Desktop.** A hammer icon (🔨) in the chat UI confirms the server is connected.

### Usage

Ask Claude Desktop questions in plain English:

> *"What schemas are available in the Iceberg catalog?"*
> *"How many rows are in the california_wine_production table?"*
> *"What are the top wine-producing regions by volume?"*

Claude will automatically write and execute the necessary SQL queries against your live data.
