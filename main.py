import asyncio
import os
from dotenv import load_dotenv
from modules.database import (
    initialise_duckdb_database,
    load_companies_into_db_table,
    write_db_table_to_csv,
)
from modules.api_client import fetch_companies
from modules.helper_functions import (
    construct_graphql_query,
    read_ids_from_csv,
    load_graphQL_query_fragments,
    write_company_data_to_json,
)

_ = load_dotenv()


async def main():
    # Authorise Craft API client from key stored in .env file
    API_KEY = os.getenv("KEY_CRAFT_SOLENG", "DEFAULT")

    # Construct graphql query string for the Craft API post request
    fragments = load_graphQL_query_fragments()
    query = construct_graphql_query(fragments)

    # Read list of company ids from csv file
    all_ids = read_ids_from_csv("all_ids.csv")

    # Fetch company data for each id in the list using the defined query string
    company_results = await fetch_companies(query, all_ids, API_KEY)

    # Write company results to json file
    companies_json = write_company_data_to_json(company_results)

    # Create duckDB database for convenient processing. Creates a file with .db extension in root directory
    company_db = "company_data.db"
    company_db = initialise_duckdb_database(database_file_path=company_db)

    # Import company data into a DuckDB database for easier manipulation and analysis
    companies_table_name = load_companies_into_db_table(
        companies_file_path=companies_json, database_file_path=company_db
    )

    # # Write company data to csv file
    _ = write_db_table_to_csv(company_db, companies_table_name)


if __name__ == "__main__":
    asyncio.run(main())
