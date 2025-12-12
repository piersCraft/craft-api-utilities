from typing import Any
import duckdb as ddb
import tempfile
from pydantic import Json


class DuckDbClient:
    def __init__(self, database_path: str = ":memory:"):
        """
        Initialize DuckDB client.

        Args:
            database_path: Path to database file. Use ":memory:" for in-memory DB.
        """
        self.database_path: str = database_path
        self.connection: ddb.DuckDBPyConnection = ddb.connect(database_path)

    def db_write_json_to_table(self, data: Json[Any]) -> None:
        """Write json data to duckdb table using temporary file method"""

        # Write JSON to temp file and load
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            _ = f.write(data)
            temp_path = f.name

        _ = self.connection.execute(
            f"CREATE OR REPLACE TABLE raw AS SELECT * FROM '{temp_path}'"
        )

    def unpack_company_data(self) -> None:
        """Unpack nested company fields to columns from raw file"""

        _ = self.connection.execute(
            """
            CREATE OR REPLACE TABLE
                companies
            AS SELECT
                unnest(
                    results, max_depth:=4
                )
            FROM
                raw
            ;
            """
        )

    # TODO: Risk scan calculations
    def calculate_risk_scan_columns(self) -> None:
        """Replicate risk scan columns"""

        pass

    # TODO: Join tables on id
    def join_tables(self, left_id: str, right_id: str) -> None:
        """Replicate risk scan columns"""

        pass

    # TODO: Export results to csv
    def export_table_to_csv(self) -> None:
        """Replicate risk scan columns"""

        pass

    def summarize_table(self, table_name: str) -> Any:
        """Create summary statistics to describe a table"""

        return self.connection.sql(f"""SUMMARIZE {table_name}""").show()

    def close(self) -> None:
        """Close the database connection."""

        if self.connection:
            self.connection.close()
