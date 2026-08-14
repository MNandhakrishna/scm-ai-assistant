TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inventory_low_stock",
            "description": (
                "Get current products whose inventory is below "
                "their reorder point."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of products to return.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inventory_summary",
            "description": (
                "Get current inventory statistics grouped by warehouse."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "product_demand",
            "description": (
                "Get historical units sold and demand forecast "
                "for a specific SKU."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sku_id": {
                        "type": "string",
                        "description": "SKU identifier, for example SKU_2."
                    },
                    "warehouse_id": {
                        "type": "string",
                        "description": "Optional warehouse identifier, for example WH_3."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recent demand records to return. Use a small value such as 10, 20, or 30."
                    }
                },
                "required": ["sku_id"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "high_demand_products",
            "description": (
                "Get products with the highest current demand forecast."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of products to return.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "demand_summary",
            "description": (
                "Get current demand statistics grouped by warehouse."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restock_recommendations",
            "description": (
                "Get the current products that require restocking "
                "and their recommended order quantities."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


from src.agents.tool_definitions import (
    inventory_low_stock,
    inventory_summary,
    product_demand,
    high_demand_products,
    demand_summary,
    restock_recommendations,
)


TOOL_FUNCTIONS = {
    "inventory_low_stock": inventory_low_stock,
    "inventory_summary": inventory_summary,
    "product_demand": product_demand,
    "high_demand_products": high_demand_products,
    "demand_summary": demand_summary,
    "restock_recommendations": restock_recommendations,
}

INVENTORY_TOOLS = [
    TOOLS[0],
    TOOLS[1],
]

DEMAND_TOOLS = [
    TOOLS[2],
    TOOLS[3],
    TOOLS[4],
]

RESTOCK_TOOLS = [
    TOOLS[5],
]