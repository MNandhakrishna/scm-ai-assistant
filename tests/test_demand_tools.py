from src.tools.demand_tools import (
    get_product_demand,
    get_high_demand_products,
    get_demand_summary,
)


def test_product_demand_filters_by_sku():
    result = get_product_demand(
        sku_id="SKU_2",
        limit=10,
    )

    assert not result.empty

    assert all(
        result["SKU_ID"] == "SKU_2"
    )


def test_product_demand_limit_is_respected():
    result = get_product_demand(
        sku_id="SKU_2",
        limit=5,
    )

    assert len(result) <= 5


def test_product_demand_filters_by_warehouse():
    result = get_product_demand(
        sku_id="SKU_2",
        warehouse_id="WH_3",
        limit=10,
    )

    assert not result.empty

    assert all(
        result["SKU_ID"] == "SKU_2"
    )

    assert all(
        result["Warehouse_ID"] == "WH_3"
    )


def test_high_demand_products_are_sorted():
    result = get_high_demand_products(
        limit=10
    )

    assert not result.empty

    forecasts = result[
        "Demand_Forecast"
    ].tolist()

    assert forecasts == sorted(
        forecasts,
        reverse=True,
    )


def test_high_demand_limit_is_respected():
    result = get_high_demand_products(
        limit=5
    )

    assert len(result) <= 5


def test_demand_summary_contains_warehouses():
    result = get_demand_summary()

    assert not result.empty

    assert "Warehouse_ID" in result.columns

    assert "total_demand_forecast" in result.columns