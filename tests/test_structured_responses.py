from src.schemas.response_builder import build_response_from_tool
from src.schemas.responses import (
    LowStockResponse,
    RestockResponse,
    DemandResponse,
)


def test_low_stock_response():
    tool_result = [
        {
            "SKU_ID": "SKU_2",
            "Warehouse_ID": "WH_1",
            "Inventory_Level": 299,
            "Reorder_Point": 319,
        },
        {
            "SKU_ID": "SKU_19",
            "Warehouse_ID": "WH_2",
            "Inventory_Level": 278,
            "Reorder_Point": 295,
        },
    ]

    response = build_response_from_tool(
        "inventory_low_stock",
        tool_result,
    )

    assert isinstance(response, LowStockResponse)

    assert response.answer_type == "low_stock"

    assert len(response.items) == 2

    assert response.items[0].sku_id == "SKU_2"
    assert response.items[0].warehouse_id == "WH_1"

    assert response.items[0].inventory_level == 299
    assert response.items[0].reorder_point == 319
    assert response.items[0].stock_gap == 20


def test_restock_response():
    tool_result = [
        {
            "SKU_ID": "SKU_27",
            "Warehouse_ID": "WH_4",
            "Inventory_Level": 315,
            "Required_Inventory": 496,
            "Recommended_Order_Quantity": 181,
        },
        {
            "SKU_ID": "SKU_29",
            "Warehouse_ID": "WH_2",
            "Inventory_Level": 402,
            "Required_Inventory": 534.24,
            "Recommended_Order_Quantity": 132.24,
        },
    ]

    response = build_response_from_tool(
        "restock_recommendations",
        tool_result,
    )

    assert isinstance(response, RestockResponse)

    assert response.answer_type == "restocking"

    assert len(response.items) == 2

    first = response.items[0]

    assert first.sku_id == "SKU_27"
    assert first.warehouse_id == "WH_4"
    assert first.recommended_quantity == 181
    assert first.current_inventory == 315
    assert first.required_inventory == 496

    second = response.items[1]

    assert second.sku_id == "SKU_29"
    assert second.recommended_quantity == 132.24


def test_high_demand_response():
    tool_result = [
        {
            "SKU_ID": "SKU_27",
            "Warehouse_ID": "WH_4",
            "Demand_Forecast": 41.52,
        },
        {
            "SKU_ID": "SKU_10",
            "Warehouse_ID": "WH_5",
            "Demand_Forecast": 35.62,
        },
    ]

    response = build_response_from_tool(
        "high_demand_products",
        tool_result,
    )

    assert isinstance(response, DemandResponse)

    assert response.answer_type == "demand"

    assert len(response.items) == 2

    assert response.items[0].sku_id == "SKU_27"
    assert response.items[0].demand_forecast == 41.52


def test_product_demand_response():
    tool_result = [
        {
            "SKU_ID": "SKU_27",
            "Warehouse_ID": "WH_4",
            "Units_Sold": 35,
            "Demand_Forecast": 41.52,
        }
    ]

    response = build_response_from_tool(
        "product_demand",
        tool_result,
    )

    assert isinstance(response, DemandResponse)

    assert response.answer_type == "demand"

    assert len(response.items) == 1

    item = response.items[0]

    assert item.sku_id == "SKU_27"
    assert item.warehouse_id == "WH_4"
    assert item.units_sold == 35
    assert item.demand_forecast == 41.52


def test_unknown_tool_returns_none():
    response = build_response_from_tool(
        "unknown_tool",
        [],
    )

    assert response is None