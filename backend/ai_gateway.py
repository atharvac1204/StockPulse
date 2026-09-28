import os
import json
import logging
import requests
from typing import Optional, Dict, Any
from models import Product
from sqlalchemy.orm import Session
from commerce_engine import RuleBasedCommerceStrategy
        
    def calculate_pricing(self, product: Product, db: Session, trigger_reason: str) -> Optional[dict]:
        """
        Calculate pricing recommendation using Gemini AI
        """
        if not self.enabled:
            logger.warning("Gemini API key not configured, falling back to rule-based strategy")
            return None
            
        try:
            # Calculate category average demand velocity
            category_avg_demand = RuleBasedCommerceStrategy()._calculate_category_average_demand(product.category, db)
            
            # Prepare context for Gemini
            context = {
                "product_name": product.name,
                "category": product.category,
                "current_price": float(product.current_price),
                "current_stock": product.stock_level,
                "reorder_threshold": product.reorder_threshold,
                "demand_velocity": float(product.demand_velocity),
                "category_average_demand_velocity": category_avg_demand,
                "trigger_reason": trigger_reason
            }
            
            # Prepare the prompt for Gemini
            prompt = f"""
You are an inventory management expert. Based on the following product information, 
provide a pricing recommendation.

Product Information:
- Name: {context['product_name']}
- Category: {context['category']}
- Current Price: ${context['current_price']}
- Current Stock: {context['current_stock']}
- Reorder Threshold: {context['reorder_threshold']}
- Demand Velocity: {context['demand_velocity']}
- Category Average Demand Velocity: {context['category_average_demand_velocity']}
- Trigger Reason: {context['trigger_reason']}

Based on this information, determine:
1. Should the price be increased, decreased, or held?
2. What is the recommended new price?
3. How confident are you in this recommendation (0-1 scale)?
4. Explain your reasoning.

Respond ONLY with a JSON object in this exact format:
{{
  "recommended_price": 0.0,
  "direction": "INCREASE|DECREASE|HOLD",
  "confidence": 0.0,
  "reasoning": "string"
}}
"""

            # Call Gemini API
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            url = f"{self.api_url}?key={self.api_key}"
            
            logger.info(f"Calling Gemini API for pricing recommendation for product {product.id}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract the text response
                if "candidates" in response_data and len(response_data["candidates"]) > 0:
                    content = response_data["candidates"][0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        text_response = content["parts"][0]["text"]
                        
                        # Try to parse as JSON
                        try:
                            # Clean up the response to ensure it's valid JSON
                            # Remove any markdown formatting
                            cleaned_text = text_response.strip()
                            if cleaned_text.startswith("```json"):
                                cleaned_text = cleaned_text[7:]
                            if cleaned_text.endswith("```"):
                                cleaned_text = cleaned_text[:-3]
                            
                            ai_response = json.loads(cleaned_text)
                            
                            # Validate response
                            if self._validate_pricing_response(ai_response):
                                logger.info(f"Successfully received valid pricing recommendation from Gemini for product {product.id}")
                                return ai_response
                            else:
                                logger.warning(f"Invalid response format from Gemini for product {product.id}, falling back to rule-based strategy")
                                return None
    
    def calculate_reorder(self, product: Product, db: Session, trigger_reason: str) -> Optional[dict]:
        """
        Calculate reorder recommendation using Gemini AI
        """
        if not self.enabled:
            logger.warning("Gemini API key not configured, falling back to rule-based strategy")
            return None
            
        try:
            # Calculate category average demand velocity
            category_avg_demand = RuleBasedCommerceStrategy()._calculate_category_average_demand(product.category, db)
            
            # Prepare context for Gemini
            context = {
                "product_name": product.name,
                "category": product.category,
                "current_stock": product.stock_level,
                "reorder_threshold": product.reorder_threshold,
                "demand_velocity": float(product.demand_velocity),
                "category_average_demand_velocity": category_avg_demand,
                "trigger_reason": trigger_reason
            }
            
            # Prepare the prompt for Gemini
            prompt = f"""
You are an inventory management expert. Based on the following product information,
provide a reorder recommendation.

Product Information:
- Name: {context['product_name']}
- Category: {context['category']}
- Current Stock: {context['current_stock']}
- Reorder Threshold: {context['reorder_threshold']}
- Demand Velocity: {context['demand_velocity']}
- Category Average Demand Velocity: {context['category_average_demand_velocity']}
- Trigger Reason: {context['trigger_reason']}

Based on this information, determine:
1. How many units should be reordered?
2. How confident are you in this recommendation (0-1 scale)?
3. Explain your reasoning.

Respond ONLY with a JSON object in this exact format:
{{
  "recommended_quantity": 0,
  "confidence": 0.0,
  "reasoning": "string"
}}
"""

            # Call Gemini API
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            url = f"{self.api_url}?key={self.api_key}"
            
            logger.info(f"Calling Gemini API for reorder recommendation for product {product.id}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract the text response
                if "candidates" in response_data and len(response_data["candidates"]) > 0:
                    content = response_data["candidates"][0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        text_response = content["parts"][0]["text"]
                        
                        # Try to parse as JSON
                        try:
                            # Clean up the response to ensure it's valid JSON
                            # Remove any markdown formatting
                            cleaned_text = text_response.strip()
                            if cleaned_text.startswith("```json"):
                                cleaned_text = cleaned_text[7:]
                            if cleaned_text.endswith("```"):
                                cleaned_text = cleaned_text[:-3]
                            
                            ai_response = json.loads(cleaned_text)
                            
                            # Validate response
                            if self._validate_reorder_response(ai_response):
                                logger.info(f"Successfully received valid reorder recommendation from Gemini for product {product.id}")
                                return ai_response
                            else:
                                logger.warning(f"Invalid response format from Gemini for product {product.id}, falling back to rule-based strategy")
                                return None
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse Gemini response as JSON for product {product.id}: {str(e)}, falling back to rule-based strategy")
                            return None
    
    def _validate_pricing_response(self, response: dict) -> bool:
        """Validate pricing response from AI"""
        required_fields = ['recommended_price', 'direction', 'confidence', 'reasoning']
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Missing required field in AI pricing response: {field}")
                return False
                
        # Validate field values
        if not isinstance(response['recommended_price'], (int, float)) or response['recommended_price'] <= 0:
            logger.warning("Invalid recommended_price in AI pricing response")
            return False
            
        if response['direction'] not in ['INCREASE', 'DECREASE', 'HOLD']:
            logger.warning("Invalid direction in AI pricing response")
            return False
            
        if not isinstance(response['confidence'], (int, float)) or response['confidence'] < 0 or response['confidence'] > 1:
            logger.warning("Invalid confidence in AI pricing response")
            return False
            
        if not response['reasoning'] or not isinstance(response['reasoning'], str):
            logger.warning("Invalid reasoning in AI pricing response")
            return False
            
        return True
    
    def _validate_reorder_response(self, response: dict) -> bool:
        """Validate reorder response from AI"""
        required_fields = ['recommended_quantity', 'confidence', 'reasoning']
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Missing required field in AI reorder response: {field}")
                return False
                
        # Validate field values
        if not isinstance(response['recommended_quantity'], int) or response['recommended_quantity'] <= 0:
            logger.warning("Invalid recommended_quantity in AI reorder response")
            return False
            
        if not isinstance(response['confidence'], (int, float)) or response['confidence'] < 0 or response['confidence'] > 1:
            logger.warning("Invalid confidence in AI reorder response")
            return False
            
        if not response['reasoning'] or not isinstance(response['reasoning'], str):
            logger.warning("Invalid reasoning in AI reorder response")
            return False
            
        return True
                else:
                    logger.warning(f"No candidates in Gemini response for product {product.id}, falling back to rule-based strategy")
                    return None
            else:
                logger.error(f"Gemini API returned status code {response.status_code} for product {product.id}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Gemini API timeout for product {product.id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request error for product {product.id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Gemini reorder calculation for product {product.id}: {str(e)}")
            return None
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse Gemini response as JSON for product {product.id}: {str(e)}, falling back to rule-based strategy")
                            return None
                else:
                    logger.warning(f"No candidates in Gemini response for product {product.id}, falling back to rule-based strategy")
                    return None
            else:
                logger.error(f"Gemini API returned status code {response.status_code} for product {product.id}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Gemini API timeout for product {product.id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request error for product {product.id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Gemini pricing calculation for product {product.id}: {str(e)}")
            return None

# Configure logging
logger = logging.getLogger(__name__)

class AIGateway:
    """AI Gateway for interacting with Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = bool(self.api_key)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"