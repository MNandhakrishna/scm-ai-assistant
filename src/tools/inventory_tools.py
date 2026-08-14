from src.data.database import get_connection, create_inventory_view


def get_latest_date():
    """Return the latest date available in the dataset."""

    connection = get_connection()
    create_inventory_view(connection)

    query = """
        SELECT MAX(Date)
        FROM supply_chain
    """

    result = connection.execute(query).fetchone()

    connection.close()

    return result[0]


def get_current_inventory():
    """
    Return the latest inventory record for each SKU and warehouse.
    """

    connection = get_connection()
    create_inventory_view(connection)

    query = """
        WITH latest_records AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY SKU_ID, Warehouse_ID
                    ORDER BY Date DESC
                ) AS row_num
            FROM supply_chain
        )

        SELECT
            Date,
            SKU_ID,
            Warehouse_ID,
            Supplier_ID,
            Inventory_Level,
            Reorder_Point,
            Demand_Forecast,
            Supplier_Lead_Time_Days,
            Order_Quantity,
            Unit_Cost,
            Unit_Price
        FROM latest_records
        WHERE row_num = 1
        ORDER BY Warehouse_ID, SKU_ID
    """

    result = connection.execute(query).fetchdf()

    connection.close()

    return result


def get_current_low_stock(limit=20):
    """
    Return products that are currently below their reorder point.
    """

    connection = get_connection()
    create_inventory_view(connection)

    query = """
        WITH latest_records AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY SKU_ID, Warehouse_ID
                    ORDER BY Date DESC
                ) AS row_num
            FROM supply_chain
        )

        SELECT
            Date,
            SKU_ID,
            Warehouse_ID,
            Supplier_ID,
            Inventory_Level,
            Reorder_Point,
            Demand_Forecast,
            Supplier_Lead_Time_Days,
            Order_Quantity,
            (Reorder_Point - Inventory_Level) AS Stock_Gap
        FROM latest_records
        WHERE row_num = 1
          AND Inventory_Level < Reorder_Point
        ORDER BY Stock_Gap DESC
        LIMIT ?
    """

    result = connection.execute(query, [limit]).fetchdf()

    connection.close()

    return result


def get_inventory_summary():
    """
    Return a summary of the current inventory situation by warehouse.
    """

    connection = get_connection()
    create_inventory_view(connection)

    query = """
        WITH latest_records AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY SKU_ID, Warehouse_ID
                    ORDER BY Date DESC
                ) AS row_num
            FROM supply_chain
        ),

        current_inventory AS (
            SELECT *
            FROM latest_records
            WHERE row_num = 1
        )

        SELECT
            Warehouse_ID,
            COUNT(*) AS total_products,
            SUM(
                CASE
                    WHEN Inventory_Level < Reorder_Point
                    THEN 1
                    ELSE 0
                END
            ) AS low_stock_products,
            SUM(
                CASE
                    WHEN Inventory_Level < Reorder_Point
                    THEN Reorder_Point - Inventory_Level
                    ELSE 0
                END
            ) AS total_stock_gap,
            ROUND(AVG(Inventory_Level), 2) AS average_inventory
        FROM current_inventory
        GROUP BY Warehouse_ID
        ORDER BY total_stock_gap DESC
    """

    result = connection.execute(query).fetchdf()

    connection.close()

    return result


if __name__ == "__main__":

    latest_date = get_latest_date()

    print(f"=== LATEST DATA DATE ===")
    print(latest_date)

    print("\n=== CURRENT LOW STOCK ===")

    low_stock = get_current_low_stock(limit=20)
    print(low_stock.to_string(index=False))

    print("\n=== CURRENT INVENTORY SUMMARY ===")

    summary = get_inventory_summary()
    print(summary.to_string(index=False))