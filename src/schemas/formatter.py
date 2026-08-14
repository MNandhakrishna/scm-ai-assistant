from typing import Any
from src.schemas.responses import (
    LowStockResponse,
    RestockResponse,
    InventoryRiskResponse,
    DemandResponse,
    GeneralResponse,
)



def format_scm_response(response):
    """
    Convert a validated SCM response into display text.
    """

    if isinstance(response, LowStockResponse):

        lines = [
            response.summary,
            "",
        ]

        for item in response.items:

            lines.append(
                f"- {item.sku_id} "
                f"({item.warehouse_id}) - "
                f"Inventory: {item.inventory_level:g}, "
                f"Reorder Point: {item.reorder_point:g}, "
                f"Stock Gap: {item.stock_gap:g}"
            )

        return "\n".join(lines)

    if isinstance(response, RestockResponse):

        lines = [
            response.summary,
            "",
        ]

        for item in response.items:

            lines.append(
                f"- {item.sku_id} "
                f"({item.warehouse_id}) - "
                f"Recommended Order: "
                f"{item.recommended_quantity:g} units, "
                f"Current Inventory: "
                f"{item.current_inventory:g}, "
                f"Required Inventory: "
                f"{item.required_inventory:g}"
            )

        return "\n".join(lines)

    if isinstance(response, InventoryRiskResponse):

        return (
            f"{response.summary}\n\n"
            f"- Warehouse: {response.warehouse_id}\n"
            f"- Stock Gap: {response.stock_gap:g}"
        )

    if isinstance(response, DemandResponse):

        lines = [
            response.summary,
            "",
        ]

        for item in response.items:

            line = f"- {item.sku_id}"

            if item.warehouse_id:
                line += f" ({item.warehouse_id})"

            if item.units_sold is not None:
                line += f" - Units Sold: {item.units_sold:g}"

            if item.demand_forecast is not None:
                line += (
                    f" - Demand Forecast: "
                    f"{item.demand_forecast:g}"
                )

            lines.append(line)

        return "\n".join(lines)

    if isinstance(response, GeneralResponse):

        return response.summary

    raise TypeError(
        f"Unsupported SCM response type: "
        f"{type(response).__name__}"
    )