from src.tools.inventory_tools import get_current_low_stock


def test_low_stock_products_are_below_reorder_point():
    result = get_current_low_stock(limit=10)

    assert not result.empty

    for _, row in result.iterrows():
        assert row["Inventory_Level"] < row["Reorder_Point"]


def test_low_stock_limit_is_respected():
    result = get_current_low_stock(limit=5)

    assert len(result) <= 5