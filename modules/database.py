from typing import Any
import pandas as pd
from pandas import DataFrame
import duckdb as ddb


# Initialise duckDB client with a persistent database
def initialise_duckdb_database(database_file_path: str = "company_data_store.db"):
    """Initialise persistent duckDB database"""
    _ = ddb.connect(database_file_path)

    return database_file_path


# Load company data into a database table
def load_companies_into_db_table(
    companies_file_path: str,
    table_name: str = "companies",
    database_file_path: str = ":memory:",
):
    """
    Load a list of companies into an in-memory DuckDB table.

    Args:
        database_file_path: Path of the database to connect to. Defaults to in memory
        companies_filepath: List of companies to load

    Returns:
        List of tuples containing the first 5 rows
    """
    # connect to the database
    client = ddb.connect(database_file_path)
    # read json data and unpack the companies list to records
    client.execute(
        f"""CREATE OR REPLACE TABLE json_intake AS SELECT * FROM read_json({companies_file_path}, maximum_object_size=100000000)"""
    )
    client.execute(
        f"""CREATE OR REPLACE TABLE companies_temp AS SELECT UNNEST(companies, recursive := true), FROM json_intake"""
    )
    client.execute(
        f"""CREATE OR REPLACE TABLE {table_name} AS SELECT * EXCLUDE(security_ratings, id_1, datasets), security_ratings[1].grade as latest_security_rating_grade, security_ratings[1].datetime as latest_security_rating_date FROM companies_temp"""
    )
    # Display the first five rows of the company table
    result = client.sql(f"""SELECT * FROM {table_name} LIMIT 5""")
    result.show()

    return table_name


# Save a database table to .csv
def write_db_table_to_csv(database_file_path: str, table_name: str):
    """Export table to .csv file"""
    client = ddb.connect(database_file_path)
    client.sql(f"""SELECT * FROM {table_name}""").write_csv(f"{table_name}.csv")

    return table_name
