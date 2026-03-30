load iceberg;

CREATE SECRET iceberg_secret (
    TYPE iceberg,
    CLIENT_ID (GETENV ('ICEBERG_CLIENT_ID')),
    CLIENT_SECRET (GETENV ('ICEBERG_CLIENT_SECRET')),
    SCOPE (GETENV ('ICEBERG_SCOPE')),
    ENDPOINT (GETENV ('ICEBERG_ENDPOINT'))
);

LOAD httpfs;

SET
    s3_access_key_id = (GETENV ('AWS_ACCESS_KEY_ID'));

SET
    s3_secret_access_key = (GETENV ('AWS_SECRET_ACCESS_KEY'));

SET
    s3_session_token = (GETENV ('AWS_SESSION_TOKEN'));

SET
    s3_region = (GETENV ('AWS_REGION'));

SET
    s3_url_style = 'vhost';

SET
    http_keep_alive = false;

ATTACH '${ICEBERG_CATALOG_NAME}' AS iceberg_catalog (TYPE iceberg, SECRET iceberg_secret);

-- SELECT schema_name FROM information_schema.schemata WHERE catalog_name = 'iceberg_catalog';
-- SHOW TABLES FROM iceberg_catalog.mb_sql_10022026_agriculture;
-- select count(*) from iceberg_catalog.mb_sql_10022026_agriculture.california_wine_production;