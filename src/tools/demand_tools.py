from src.data.database import get_connection, create_inventory_view


def get_product_demand(
    sku_id,
    warehouse_id=None,
    limit=30
):
    """
    Return recent demand history for a specific SKU.

    By default, only the latest 30 records are returned.
    """

    connection = get_connection()
    create_inventory_view(connection)

    if warehouse_id:
        query = """
            SELECT
                Date,
                SKU_ID,
                Warehouse_ID,
                Units_Sold,
                Demand_Forecast
            FROM supply_chain
            WHERE SKU_ID = ?
              AND Warehouse_ID = ?
            ORDER BY Date DESC
            LIMIT ?
        """

        result = connection.execute(
            query,
            [sku_id, warehouse_id, limit]
        ).fetchdf()

    else:
        query = """
            SELECT
                Date,
                SKU_ID,
                Warehouse_ID,
                Units_Sold,
                Demand_Forecast
            FROM supply_chain
            WHERE SKU_ID = ?
            ORDER BY Date DESC
            LIMIT ?
        """

        result = connection.execute(
            query,
            [sku_id, limit]
        ).fetchdf()

    connection.close()

    return result.sort_values(
        ["Date", "Warehouse_ID"]
    )


def get_high_demand_products(limit=10):
    """
    Return products with the highest current demand forecast.
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
            Units_Sold,
            Demand_Forecast
        FROM latest_records
        WHERE row_num = 1
        ORDER BY Demand_Forecast DESC
        LIMIT ?
    """

    result = connection.execute(query, [limit]).fetchdf()

    connection.close()

    return result


def get_demand_summary():
    """
    Return demand statistics by warehouse using the latest available data.
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
            Warehouse_ID,
            COUNT(*) AS products,
            ROUND(AVG(Units_Sold), 2) AS average_units_sold,
            ROUND(AVG(Demand_Forecast), 2) AS average_demand_forecast,
            ROUND(SUM(Demand_Forecast), 2) AS total_demand_forecast
        FROM latest_records
        WHERE row_num = 1
        GROUP BY Warehouse_ID
        ORDER BY total_demand_forecast DESC
    """

    result = connection.execute(query).fetchdf()

    connection.close()

    return result


if __name__ == "__main__":

    print("=== HIGH DEMAND PRODUCTS ===")

    high_demand = get_high_demand_products(limit=10)
    print(high_demand.to_string(index=False))

    print("\n=== DEMAND SUMMARY ===")

    summary = get_demand_summary()
    print(summary.to_string(index=False))

    print("\n=== SKU_2 DEMAND HISTORY ===")

    sku_demand = get_product_demand("SKU_2")
    print(sku_demand.tail(10).to_string(index=False))