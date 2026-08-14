from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "supply_chain_dataset.csv"


def get_connection():
    """Create a DuckDB connection."""
    return duckdb.connect()


def create_inventory_view(connection):
    """Create a DuckDB view over the SCM dataset."""

    connection.execute(
        f"""
        CREATE OR REPLACE VIEW supply_chain AS
        SELECT *
        FROM read_csv_auto('{DATA_FILE.as_posix()}')
        """
    )


def test_connection():
    """Load the dataset and display basic information."""

    connection = get_connection()

    create_inventory_view(connection)

    result = connection.execute(
        """
        SELECT
            COUNT(*) AS total_records
        FROM supply_chain
        """
    ).fetchone()

    print(f"Total records: {result[0]:,}")

    connection.close()


if __name__ == "__main__":
    test_connection()