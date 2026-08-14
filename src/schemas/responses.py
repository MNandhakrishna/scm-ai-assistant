from typing import Literal

from pydantic import BaseModel, Field


class LowStockItem(BaseModel):
    sku_id: str
    warehouse_id: str
    inventory_level: float
    reorder_point: float
    stock_gap: float


class LowStockResponse(BaseModel):
    answer_type: Literal["low_stock"]
    summary: str
    items: list[LowStockItem] = Field(
        default_factory=list
    )


class RestockItem(BaseModel):
    sku_id: str
    warehouse_id: str
    recommended_quantity: float
    current_inventory: float
    required_inventory: float


class RestockResponse(BaseModel):
    answer_type: Literal["restocking"]
    summary: str
    items: list[RestockItem] = Field(
        default_factory=list
    )


class InventoryRiskResponse(BaseModel):
    answer_type: Literal["inventory_risk"]
    summary: str
    warehouse_id: str
    stock_gap: float


class DemandItem(BaseModel):
    sku_id: str
    warehouse_id: str | None = None
    demand_forecast: float | None = None
    units_sold: float | None = None


class DemandResponse(BaseModel):
    answer_type: Literal["demand"]
    summary: str
    items: list[DemandItem] = Field(
        default_factory=list
    )


class GeneralResponse(BaseModel):
    answer_type: Literal["general"]
    summary: str