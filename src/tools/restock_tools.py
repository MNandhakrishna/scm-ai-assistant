from src.data.database import get_connection, create_inventory_view


def get_restock_recommendations(
    safety_stock_days=2,
    limit=20
):
    """
    Calculate replenishment recommendations.

    A product is returned only when its current inventory
    is below the calculated required inventory.
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
        ),

        calculations AS (
            SELECT
                *,
                Demand_Forecast * Supplier_Lead_Time_Days
                    AS Lead_Time_Demand,

                Demand_Forecast * ?
                    AS Safety_Stock,

                (
                    Demand_Forecast * Supplier_Lead_Time_Days
                    +
                    Demand_Forecast * ?
                ) AS Required_Inventory

            FROM current_inventory
        ),

        recommendations AS (
            SELECT
                *,
                CEIL(
                    GREATEST(
                        Required_Inventory - Inventory_Level,
                        0
                    )
                ) AS Recommended_Order_Quantity

            FROM calculations
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

            ROUND(Lead_Time_Demand, 2)
                AS Lead_Time_Demand,

            ROUND(Safety_Stock, 2)
                AS Safety_Stock,

            ROUND(Required_Inventory, 2)
                AS Required_Inventory,

            Recommended_Order_Quantity

        FROM recommendations

        WHERE Recommended_Order_Quantity > 0

        ORDER BY Recommended_Order_Quantity DESC

        LIMIT ?
    """

    result = connection.execute(
        query,
        [
            safety_stock_days,
            safety_stock_days,
            limit
        ]
    ).fetchdf()

    connection.close()

    return result

if __name__ == "__main__":

    print("=== RESTOCK RECOMMENDATIONS ===")

    recommendations = get_restock_recommendations(
        safety_stock_days=2,
        limit=20
    )

    if recommendations.empty:
        print("No products currently require restocking.")
    else:
        print(
            recommendations.to_string(index=False)
        )