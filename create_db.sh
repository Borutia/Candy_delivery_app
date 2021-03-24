#!/bin/bash
psql -c "CREATE USER candy_delivery_app WITH PASSWORD 'secret';"
psql -c "ALTER ROLE candy_delivery_app SET client_encoding to 'utf8';"
psql -c "ALTER ROLE candy_delivery_app SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE candy_delivery_app SET timezone to 'UTC';"
psql -c "CREATE DATABASE candy_delivery_app_db WITH OWNER candy_delivery_app;"
psql -c "ALTER USER candy_delivery_app CREATEDB;"