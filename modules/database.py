import duckdb as ddb
import tempfile
import pyarrow as pa
from pyarrow import Table
from pydantic import Json
from typing import Any


class DuckDbClient:
    def __init__(self, database_path: str):
        """
        Initialize DuckDB client.

        Args:
            database_path: Path to database file. Use ":memory:" for in-memory DB.
        """

        self.database_path: str = database_path
        self.connection: ddb.DuckDBPyConnection = ddb.connect(database_path)

    def create_table_from_arrow(
        self, target_table_name: str, arrow_data: Table
    ) -> None:
        """Import PyArrow table"""

        _ = self.connection.sql(
            f"CREATE OR REPLACE TABLE {target_table_name} AS SELECT * FROM arrow_table"
        )

    def create_table_from_json(self, table_name: str, data: Json[Any]) -> None:
        """Write json data to duckdb table using temporary file method"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            _ = f.write(data)
            temp_path = f.name

        _ = self.connection.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_json('{temp_path}',maximum_object_size=40000000)"
        )

    def export_table_to_csv(self, table_name: str, output_filepath: str) -> None:
        """Export a table to csv. Defaults to companies table"""

        _ = self.connection.execute(f"COPY {table_name} TO '{output_filepath}'")

    def close(self) -> None:
        """Close the database connection."""

        if self.connection:
            self.connection.close()

    # TODO: Risk scan calculations
    def calculate_risk_scan_columns(self, from_table: str, to_table: str) -> None:
        """Replicate risk scan columns"""

        _ = self.connection.sql(
            f"""
            CREATE OR REPLACE TABLE
                {to_table}
            AS SELECT
                id,
                display_name,
                CASE
                    WHEN security_ratings[1].grade IN ['D', 'F'] THEN TRUE
                    ELSE FALSE
                    END AS cyber_risk,
                CASE
                    WHEN common_value IN ['C', 'D', 'E'] THEN TRUE
                    ELSE FALSE
                    END AS credit_risk
            FROM
                {from_table}
            ;
            """
        )

    # TODO: Join tables on id
    def join_tables(self, left_id: str, right_id: str) -> None:
        """Replicate risk scan columns"""
        pass
