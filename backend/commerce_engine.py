import os
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Product
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommerceStrategy(ABC):
    """Abstract base class for commerce strategies"""
    
    @abstractmethod
    def calculate_pricing(self, product: Product, db: Session) -> dict:
        """Calculate pricing recommendation for a product"""
        pass
    
    @abstractmethod
    def calculate_reorder(self, product: Product) -> dict:
        """Calculate reorder recommendation for a product"""
        pass

class RuleBasedCommerceStrategy(CommerceStrategy):
    """Rule-based commerce strategy implementation"""
    
    def calculate_pricing(self, product: Product, db: Session) -> dict:
        """
        Calculate pricing recommendation based on rules:
        Rule 1: If stock_level < reorder_threshold -> increase by 10%
        Rule 2: If demand_velocity > 2 * category average -> increase by 5%
        Otherwise: Hold current price
        """
        # Calculate category average demand velocity
        category_avg_demand = self._calculate_category_average_demand(product.category, db)
        
        # Apply pricing rules
        if product.stock_level < product.reorder_threshold:
            # Rule 1: Low stock -> increase price by 10%
            recommended_price = float(product.current_price) * 1.10
            direction = "INCREASE"
            reasoning = f"Stock level ({product.stock_level}) is below reorder threshold ({product.reorder_threshold})"
            confidence = 0.9
        elif (category_avg_demand > 0 and 
              product.demand_velocity > 2 * category_avg_demand):
            # Rule 2: High demand velocity -> increase price by 5%
            recommended_price = float(product.current_price) * 1.05
            direction = "INCREASE"
            reasoning = f"Demand velocity ({product.demand_velocity}) is more than 2x category average ({category_avg_demand:.2f})"
            confidence = 0.8
        else:
            # No rule applies -> hold current price
            recommended_price = float(product.current_price)
            direction = "HOLD"
            reasoning = "No pricing rules triggered"
            confidence = 0.7
            
        return {
            "current_price": float(product.current_price),
            "recommended_price": round(recommended_price, 2),
            "direction": direction,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def calculate_reorder(self, product: Product) -> dict:
        """
        Calculate reorder recommendation based on rule:
        recommended quantity = max((reorder_threshold * 3) - stock_level, 1)
        """
        recommended_quantity = max((product.reorder_threshold * 3) - product.stock_level, 1)
        
        return {
            "current_stock": product.stock_level,
            "recommended_quantity": recommended_quantity,
            "confidence": 0.95,
            "reasoning": f"Recommended quantity calculated as max((reorder_threshold={product.reorder_threshold} × 3) - current_stock={product.stock_level}, 1)"
        }
    
    def _calculate_category_average_demand(self, category: str, db: Session) -> float:
        """Calculate average demand velocity for products in the same category"""
        result = db.query(func.avg(Product.demand_velocity)).filter(
            Product.category == category
        ).scalar()
        
        return float(result) if result is not None else 0.0

# Strategy factory
def get_commerce_strategy() -> CommerceStrategy:
    """Get the configured commerce strategy"""
    strategy_type = os.getenv("RECOMMENDATION_STRATEGY", "RULE").upper()
    
    if strategy_type == "AI":
        logger.info("Using AI commerce strategy")
        # Import here to avoid circular imports
        from ai_commerce_strategy import AICommerceStrategy
        return AICommerceStrategy()
    else:
        logger.info("Using rule-based commerce strategy")
        return RuleBasedCommerceStrategy()

# Default strategy instance
default_strategy = get_commerce_strategy()