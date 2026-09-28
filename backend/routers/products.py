from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ..database import get_db
from ..models import Product, ProductStatusEnum, PricingSuggestion, ReorderSuggestion, SuggestionStatusEnum, TriggerReasonEnum
from ..schemas import ProductCreate, ProductResponse, OrderCreate, StockUpdate, PricingRecommendation, ReorderRecommendation
from ..commerce_engine import default_strategy
from .suggestions import create_pricing_suggestion, create_reorder_suggestion
from ..schemas import PricingSuggestionCreate, ReorderSuggestionCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

def create_suggestions_for_product(db: Session, product: Product, trigger_reason: TriggerReasonEnum):
    """Create pricing and reorder suggestions for a product"""
    try:
        # Check if pending suggestions already exist for this product and trigger reason
        existing_pricing = db.query(PricingSuggestion).filter(
            PricingSuggestion.product_id == product.id,
            PricingSuggestion.trigger_reason == trigger_reason,
            PricingSuggestion.status == SuggestionStatusEnum.PENDING
        ).first()
        
        existing_reorder = db.query(ReorderSuggestion).filter(
            ReorderSuggestion.product_id == product.id,
            ReorderSuggestion.trigger_reason == trigger_reason,
            ReorderSuggestion.status == SuggestionStatusEnum.PENDING
        ).first()
        
        # Create pricing suggestion if none exists
        if not existing_pricing:
            pricing_rec = default_strategy.calculate_pricing(product, db)
            pricing_suggestion = PricingSuggestionCreate(
                product_id=product.id,
                current_price=pricing_rec["current_price"],
                recommended_price=pricing_rec["recommended_price"],
                direction=pricing_rec["direction"],
                confidence=pricing_rec["confidence"],
                reasoning=pricing_rec["reasoning"],
                trigger_reason=trigger_reason
            )
            create_pricing_suggestion(pricing_suggestion, db)
        
        # Create reorder suggestion if none exists
        if not existing_reorder:
            reorder_rec = default_strategy.calculate_reorder(product)
            reorder_suggestion = ReorderSuggestionCreate(
                product_id=product.id,
                current_stock=product.stock_level,
                recommended_quantity=reorder_rec["recommended_quantity"],
                confidence=reorder_rec["confidence"],
                reasoning=reorder_rec["reasoning"],
                trigger_reason=trigger_reason
            )
            create_reorder_suggestion(reorder_suggestion, db)
            
    except Exception as e:
        logger.error(f"Failed to create suggestions for product {product.id}: {str(e)}")

@router.post("/{product_id}/suggest-pricing", response_model=PricingRecommendation)
def suggest_pricing(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Generate pricing suggestion for a product"""
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate pricing recommendation
    recommendation = default_strategy.calculate_pricing(db_product, db)
    
    return recommendation

@router.post("/{product_id}/suggest-reorder", response_model=ReorderRecommendation)
def suggest_reorder(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Generate reorder suggestion for a product"""
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate reorder recommendation
    recommendation = default_strategy.calculate_reorder(db_product)
    
    return recommendation

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Set status based on stock level
    status = ProductStatusEnum.OUT_OF_STOCK.value if product.stock_level == 0 else ProductStatusEnum.ACTIVE.value
    
    db_product = Product(
        sku=product.sku,
        name=product.name,
        category=product.category,
        current_price=product.current_price,
        stock_level=product.stock_level,
        reorder_threshold=product.reorder_threshold,
        demand_velocity=product.demand_velocity,
        status=status
    )
    
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="SKU already exists")
        raise HTTPException(status_code=400, detail="Invalid product data")

@router.get("/", response_model=List[ProductResponse])
def get_products(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if status:
        query = query.filter(Product.status == status)
    
    if category:
        query = query.filter(Product.category == category)
    
    return query.all()

@router.post("/{product_id}/orders", response_model=ProductResponse)
def create_order(
    product_id: int,
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if quantity is available
    if order.quantity > db_product.stock_level:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Decrease stock level
    db_product.stock_level -= order.quantity
    
    # Update status based on new stock level
    if db_product.stock_level == 0:
        db_product.status = ProductStatusEnum.OUT_OF_STOCK.value
    else:
        db_product.status = ProductStatusEnum.ACTIVE.value
    
    # Commit changes
    db.commit()
    db.refresh(db_product)
    
    # Check if stock is below reorder threshold and schedule background task
    if db_product.stock_level < db_product.reorder_threshold:
        background_tasks.add_task(create_suggestions_for_product, db, db_product, TriggerReasonEnum.INVENTORY_LOW)
    
    # Check for demand spike (using 3x category average as threshold)
    from commerce_engine import RuleBasedCommerceStrategy
    category_avg_demand = RuleBasedCommerceStrategy()._calculate_category_average_demand(db_product.category, db)
    if category_avg_demand > 0 and db_product.demand_velocity > 3 * category_avg_demand:
        background_tasks.add_task(create_suggestions_for_product, db, db_product, TriggerReasonEnum.DEMAND_SPIKE)
    
    return db_product

@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    stock_update: StockUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update stock level
    db_product.stock_level = stock_update.stock_level
    
    # Update status based on new stock level
    if db_product.stock_level == 0:
        db_product.status = ProductStatusEnum.OUT_OF_STOCK.value
    else:
        db_product.status = ProductStatusEnum.ACTIVE.value
    
    # Commit changes
    db.commit()
    db.refresh(db_product)
    
    # Check if stock is below reorder threshold and schedule background task
    if db_product.stock_level < db_product.reorder_threshold:
        background_tasks.add_task(create_suggestions_for_product, db, db_product, TriggerReasonEnum.INVENTORY_LOW)
    
    # Check for demand spike (using 3x category average as threshold)
    from commerce_engine import RuleBasedCommerceStrategy
    category_avg_demand = RuleBasedCommerceStrategy()._calculate_category_average_demand(db_product.category, db)
    if category_avg_demand > 0 and db_product.demand_velocity > 3 * category_avg_demand:
        background_tasks.add_task(create_suggestions_for_product, db, db_product, TriggerReasonEnum.DEMAND_SPIKE)
    
    return db_product

@router.get("/{product_id}/pricing", response_model=PricingRecommendation)
def get_pricing_recommendation(
    product_id: int,
    db: Session = Depends(get_db)
):
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate pricing recommendation
    recommendation = default_strategy.calculate_pricing(db_product, db)
    
    return recommendation

@router.get("/{product_id}/reorder", response_model=ReorderRecommendation)
def get_reorder_recommendation(
    product_id: int,
    db: Session = Depends(get_db)
):
    # Find product by ID
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate reorder recommendation
    recommendation = default_strategy.calculate_reorder(db_product)
    
    return recommendation