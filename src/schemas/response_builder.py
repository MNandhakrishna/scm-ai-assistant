from typing import Any

from src.schemas.responses import (
    LowStockItem,
    LowStockResponse,
    RestockItem,
    RestockResponse,
    DemandItem,
    DemandResponse,
)


def build_response_from_tool(
    tool_name: str,
    tool_result: Any,
):
    """
    Convert raw SCM tool output into a validated
    structured response.

    Returns None when the tool does not yet have
    a structured response implementation.
    """

    if not isinstance(tool_result, list):
        return None

    # =====================================================
    # LOW STOCK
    # =====================================================

    if tool_name == "inventory_low_stock":

        items = []

        for row in tool_result:

            inventory_level = float(
                row["Inventory_Level"]
            )

            reorder_point = float(
                row["Reorder_Point"]
            )

            stock_gap = (
                reorder_point - inventory_level
            )

            items.append(
                LowStockItem(
                    sku_id=row["SKU_ID"],
                    warehouse_id=row["Warehouse_ID"],
                    inventory_level=inventory_level,
                    reorder_point=reorder_point,
                    stock_gap=stock_gap,
                )
            )

        return LowStockResponse(
            answer_type="low_stock",
            summary=(
                f"{len(items)} products are currently "
                "below their reorder point."
            ),
            items=items,
        )

    # =====================================================
    # RESTOCKING
    # =====================================================

    if tool_name == "restock_recommendations":

        items = []

        for row in tool_result:

            items.append(
                RestockItem(
                    sku_id=row["SKU_ID"],
                    warehouse_id=row["Warehouse_ID"],
                    recommended_quantity=float(
                        row[
                            "Recommended_Order_Quantity"
                        ]
                    ),
                    current_inventory=float(
                        row["Inventory_Level"]
                    ),
                    required_inventory=float(
                        row["Required_Inventory"]
                    ),
                )
            )

        return RestockResponse(
            answer_type="restocking",
            summary=(
                f"{len(items)} products require "
                "replenishment."
            ),
            items=items,
        )

    # =====================================================
    # HIGH DEMAND
    # =====================================================

    if tool_name == "high_demand_products":

        items = []

        for row in tool_result:

            items.append(
                DemandItem(
                    sku_id=row["SKU_ID"],
                    warehouse_id=row.get(
                        "Warehouse_ID"
                    ),
                    demand_forecast=float(
                        row["Demand_Forecast"]
                    ),
                )
            )

        return DemandResponse(
            answer_type="demand",
            summary=(
                f"{len(items)} products have the "
                "highest demand forecasts."
            ),
            items=items,
        )

    # =====================================================
    # PRODUCT DEMAND HISTORY
    # =====================================================

    if tool_name == "product_demand":

        items = []

        for row in tool_result:

            items.append(
                DemandItem(
                    sku_id=row["SKU_ID"],
                    warehouse_id=row.get(
                        "Warehouse_ID"
                    ),
                    demand_forecast=float(
                        row["Demand_Forecast"]
                    ),
                    units_sold=float(
                        row["Units_Sold"]
                    ),
                )
            )

        return DemandResponse(
            answer_type="demand",
            summary=(
                f"Demand history contains "
                f"{len(items)} records."
            ),
            items=items,
        )

    return None