from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from .database import Base
import enum
from datetime import datetime

class ProductStatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    PRICE_REVIEW_PENDING = "PRICE_REVIEW_PENDING"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class SuggestionStatusEnum(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class TriggerReasonEnum(enum.Enum):
    INVENTORY_LOW = "INVENTORY_LOW"
    DEMAND_SPIKE = "DEMAND_SPIKE"
    MANUAL = "MANUAL"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_price = Column(Numeric(precision=10, scale=2), nullable=False)
    stock_level = Column(Integer, nullable=False)
    reorder_threshold = Column(Integer, nullable=False)
    demand_velocity = Column(Numeric(precision=10, scale=2), nullable=False)
    status = Column(String, nullable=False)
    
    # Indexes for common query fields
    __table_args__ = (
        Index('ix_products_category', 'category'),
        Index('ix_products_status', 'status'),
    )
    
    def __init__(self, **kwargs):
        # Set status based on stock level
        if 'stock_level' in kwargs and kwargs['stock_level'] == 0:
            kwargs['status'] = ProductStatusEnum.OUT_OF_STOCK.value
        elif 'status' not in kwargs:
            kwargs['status'] = ProductStatusEnum.ACTIVE.value
        super().__init__(**kwargs)

class PricingSuggestion(Base):
    __tablename__ = "pricing_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    current_price = Column(Numeric(precision=10, scale=2), nullable=False)
    recommended_price = Column(Numeric(precision=10, scale=2), nullable=False)
    direction = Column(String, nullable=False)  # INCREASE, DECREASE, HOLD
    confidence = Column(Numeric(precision=5, scale=2), nullable=False)
    reasoning = Column(String, nullable=False)
    status = Column(SQLEnum(SuggestionStatusEnum), default=SuggestionStatusEnum.PENDING, nullable=False)
    trigger_reason = Column(SQLEnum(TriggerReasonEnum), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_pricing_suggestions_product_id', 'product_id'),
        Index('ix_pricing_suggestions_status', 'status'),
        Index('ix_pricing_suggestions_trigger_reason', 'trigger_reason'),
    )

class ReorderSuggestion(Base):
    __tablename__ = "reorder_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    current_stock = Column(Integer, nullable=False)
    recommended_quantity = Column(Integer, nullable=False)
    lead_time = Column(Integer, default=3, nullable=False)  # Default lead time in days
    confidence = Column(Numeric(precision=5, scale=2), nullable=False)
    reasoning = Column(String, nullable=False)
    status = Column(SQLEnum(SuggestionStatusEnum), default=SuggestionStatusEnum.PENDING, nullable=False)
    trigger_reason = Column(SQLEnum(TriggerReasonEnum), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_reorder_suggestions_product_id', 'product_id'),
        Index('ix_reorder_suggestions_status', 'status'),
        Index('ix_reorder_suggestions_trigger_reason', 'trigger_reason'),
    )