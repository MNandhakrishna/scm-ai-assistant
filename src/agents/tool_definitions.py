from src.tools.inventory_tools import (
    get_current_low_stock,
    get_inventory_summary,
)

from src.tools.demand_tools import (
    get_product_demand,
    get_high_demand_products,
    get_demand_summary,
)

from src.tools.restock_tools import (
    get_restock_recommendations,
)


def inventory_low_stock(limit: int = 10):
    """Return current products below their reorder point."""

    result = get_current_low_stock(limit=limit)

    return {
        "analysis_type": "LOW_STOCK_ONLY",
        "restocking_confirmed": False,
        "message": (
            "These products are below their reorder points. "
            "This identifies low-stock conditions only. "
            "It does not confirm that they require restocking "
            "and does not provide recommended order quantities."
        ),
        "products": result.to_dict(orient="records"),
    }

def inventory_summary():
    """Return the current inventory summary by warehouse."""

    result = get_inventory_summary()

    return result.to_dict(orient="records")


def product_demand(
    sku_id: str,
    warehouse_id: str = None,
    limit: int = 30
):
    """Return recent demand history for a specific product."""

    result = get_product_demand(
        sku_id=sku_id,
        warehouse_id=warehouse_id,
        limit=limit
    )

    return result.to_dict(orient="records")


def high_demand_products(limit: int = 10):
    """Return products with the highest current demand forecast."""

    result = get_high_demand_products(limit=limit)

    return result.to_dict(orient="records")


def demand_summary():
    """Return demand statistics by warehouse."""

    result = get_demand_summary()

    return result.to_dict(orient="records")


def restock_recommendations(
    safety_stock_days: int = 2,
    limit: int = 10,
):
    """Return products requiring replenishment and recommended quantities."""

    result = get_restock_recommendations(
        safety_stock_days=safety_stock_days,
        limit=limit,
    )

    columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
        "Inventory_Level",
        "Demand_Forecast",
        "Supplier_Lead_Time_Days",
        "Lead_Time_Demand",
        "Safety_Stock",
        "Required_Inventory",
        "Recommended_Order_Quantity",
    ]

    result = result[columns]

    return {
        "analysis_type": "RESTOCK_RECOMMENDATIONS",
        "restocking_confirmed": True,
        "description": (
            "These products have positive recommended "
            "order quantities and require replenishment."
        ),
        "products": result.to_dict(orient="records"),
    }