from src.tools.restock_tools import get_restock_recommendations


def test_restock_recommendations_have_positive_order_quantity():
    result = get_restock_recommendations(
        safety_stock_days=2,
        limit=10,
    )

    assert not result.empty

    for _, row in result.iterrows():
        assert row["Recommended_Order_Quantity"] > 0


def test_restock_required_inventory_is_greater_than_current_inventory():
    result = get_restock_recommendations(
        safety_stock_days=2,
        limit=10,
    )

    assert not result.empty

    for _, row in result.iterrows():
        assert (
            row["Required_Inventory"]
            > row["Inventory_Level"]
        )


def test_restock_quantity_matches_inventory_gap():
    result = get_restock_recommendations(
        safety_stock_days=2,
        limit=10,
    )

    assert not result.empty

    for _, row in result.iterrows():

        expected_quantity = (
            row["Required_Inventory"]
            - row["Inventory_Level"]
        )

        assert abs(
            row["Recommended_Order_Quantity"]
            - expected_quantity
        ) < 0.01