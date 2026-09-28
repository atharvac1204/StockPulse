from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum
from datetime import datetime

class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PRICE_REVIEW_PENDING = "PRICE_REVIEW_PENDING"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class SuggestionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class TriggerReason(str, Enum):
    INVENTORY_LOW = "INVENTORY_LOW"
    DEMAND_SPIKE = "DEMAND_SPIKE"
    MANUAL = "MANUAL"

class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    current_price: float
    stock_level: int
    reorder_threshold: int
    demand_velocity: float

    @validator('current_price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('current_price must be greater than 0')
        return v

    @validator('stock_level', 'reorder_threshold', 'demand_velocity')
    def must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Value must be greater than or equal to 0')
        return v

    @validator('sku', 'name', 'category')
    def must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    status: ProductStatus

    class Config:
        orm_mode = True

# New schemas for order/stock simulation
class OrderCreate(BaseModel):
    quantity: int

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('quantity must be a positive integer')
        return v

class StockUpdate(BaseModel):
    stock_level: int

    @validator('stock_level')
    def stock_level_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('stock_level must be a non-negative integer')
        return v

# Commerce engine schemas
class PricingRecommendation(BaseModel):
    current_price: float
    recommended_price: float
    direction: str
    confidence: float
    reasoning: str

class ReorderRecommendation(BaseModel):
    current_stock: int
    recommended_quantity: int
    confidence: float
    reasoning: str

# Suggestion schemas
class PricingSuggestionCreate(BaseModel):
    product_id: int
    current_price: float
    recommended_price: float
    direction: str
    confidence: float
    reasoning: str
    trigger_reason: TriggerReason

class PricingSuggestionUpdate(BaseModel):
    status: SuggestionStatus

class PricingSuggestionResponse(PricingSuggestionCreate):
    id: int
    status: SuggestionStatus
    created_at: datetime

    class Config:
        orm_mode = True

class ReorderSuggestionCreate(BaseModel):
    product_id: int
    current_stock: int
    recommended_quantity: int
    lead_time: int = 3
    confidence: float
    reasoning: str
    trigger_reason: TriggerReason

class ReorderSuggestionUpdate(BaseModel):
    status: SuggestionStatus

class ReorderSuggestionResponse(ReorderSuggestionCreate):
    id: int
    status: SuggestionStatus
    created_at: datetime

    class Config:
        orm_mode = True