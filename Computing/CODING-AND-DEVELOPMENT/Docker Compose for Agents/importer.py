#!/usr/bin/env python3
"""
Import SQLite database to PostgreSQL
"""
import os
import sqlite3
import psycopg2
from pgcopy import CopyManager


def import_sqlite_to_postgres():
    """Import data from SQLite to PostgreSQL"""
    sqlite_file = os.getenv("SQLITE_FILE")
    postgres_url = os.getenv("DATABASE_URL")

    if not sqlite_file or not postgres_url:
        raise ValueError("SQLITE_FILE and DATABASE_URL must be set")

    print(f"Importing {sqlite_file} to PostgreSQL...")

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(postgres_url)
    pg_cursor = pg_conn.cursor()

    # Get all tables from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()

    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        print(f"Importing table: {table_name}")

        # Get table schema
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = sqlite_cursor.fetchall()

        # Create table in PostgreSQL
        columns_def = []
        for col in columns_info:
            col_name = col[1]
            col_type = col[2]
            # Map SQLite types to PostgreSQL
            if "INT" in col_type.upper():
                pg_type = "INTEGER"
            elif "CHAR" in col_type.upper() or "TEXT" in col_type.upper():
                pg_type = "TEXT"
            elif "REAL" in col_type.upper() or "NUMERIC" in col_type.upper():
                pg_type = "NUMERIC"
            else:
                pg_type = "TEXT"
            columns_def.append(f'"{col_name}" {pg_type}')

        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_def)})"
        pg_cursor.execute(create_table_sql)

        # Copy data
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if rows:
            column_names = [col[1] for col in columns_info]
            mgr = CopyManager(pg_conn, table_name, column_names)
            mgr.copy(rows)

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_cursor.close()
    sqlite_conn.close()

    print("Import completed successfully!")


if __name__ == "__main__":
    import_sqlite_to_postgres()
