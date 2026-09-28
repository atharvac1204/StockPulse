from .models import Product
from sqlalchemy.orm import Session
from .commerce_engine import CommerceStrategy, RuleBasedCommerceStrategy
from .ai_gateway import AIGateway
import logging

logger = logging.getLogger(__name__)

class AICommerceStrategy(CommerceStrategy):
    """AI-powered commerce strategy using Gemini"""
    
    def __init__(self):
        self.ai_gateway = AIGateway()
        self.rule_strategy = RuleBasedCommerceStrategy()
    
    def calculate_pricing(self, product: Product, db: Session) -> dict:
        """
        Calculate pricing recommendation using AI with fallback to rules
        """
        # Try AI first
        ai_response = self.ai_gateway.calculate_pricing(product, db, "MANUAL")
        
        if ai_response:
            logger.info("Using AI-generated pricing recommendation")
            return ai_response
        else:
            # Fallback to rule-based strategy
            logger.info("Falling back to rule-based pricing recommendation")
            return self.rule_strategy.calculate_pricing(product, db)
    
    def calculate_reorder(self, product: Product, db: Session) -> dict:
        """
        Calculate reorder recommendation using AI with fallback to rules
        """
        # Try AI first
        ai_response = self.ai_gateway.calculate_reorder(product, db, "MANUAL")
        
        if ai_response:
            logger.info("Using AI-generated reorder recommendation")
            return ai_response
        else:
            # Fallback to rule-based strategy
            logger.info("Falling back to rule-based reorder recommendation")
            return self.rule_strategy.calculate_reorder(product)