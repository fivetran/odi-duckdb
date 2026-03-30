#!/bin/bash

cat << 'BANNER'

  ███████╗██╗██╗   ██╗███████╗████████╗██████╗  █████╗ ███╗   ██╗
  ██╔════╝██║██║   ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║
  █████╗  ██║██║   ██║█████╗     ██║   ██████╔╝███████║██╔██╗ ██║
  ██╔══╝  ██║╚██╗ ██╔╝██╔══╝     ██║   ██╔══██╗██╔══██║██║╚██╗██║
  ██║     ██║ ╚████╔╝ ███████╗   ██║   ██║  ██║██║  ██║██║ ╚████║
  ╚═╝     ╚═╝  ╚═══╝  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝

              ~ Polaris Iceberg + S3 Explorer ~

                          ___
                       __/ o \
                      (       )>   quack!
                       \_____/
                         | |
                        _|_|_

BANNER

# Load environment variables from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Run DuckDB in interactive mode, substituting shell variables in the SQL
duckdb -init <(sed "s/\${ICEBERG_CATALOG_NAME}/$ICEBERG_CATALOG_NAME/g" script.sql)
