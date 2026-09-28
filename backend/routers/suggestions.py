from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    Product, 
    PricingSuggestion, 
    ReorderSuggestion, 
    ProductStatusEnum, 
    SuggestionStatusEnum
)
from ..schemas import (
    PricingSuggestionCreate, 
    PricingSuggestionResponse, 
    ReorderSuggestionCreate, 
    ReorderSuggestionResponse,
    PricingSuggestionUpdate,
    ReorderSuggestionUpdate
)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])
def create_pricing_suggestion(
    suggestion: PricingSuggestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new pricing suggestion"""
    # Verify product exists
    db_product = db.query(Product).filter(Product.id == suggestion.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create pricing suggestion
    db_suggestion = PricingSuggestion(
        product_id=suggestion.product_id,
        current_price=suggestion.current_price,
        recommended_price=suggestion.recommended_price,
        direction=suggestion.direction,
        confidence=suggestion.confidence,
        reasoning=suggestion.reasoning,
        trigger_reason=suggestion.trigger_reason
    )
    
    try:
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create pricing suggestion: {str(e)}")

@router.post("/reorder", response_model=ReorderSuggestionResponse, status_code=201)
def create_reorder_suggestion(
    suggestion: ReorderSuggestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new reorder suggestion"""
    # Verify product exists
    db_product = db.query(Product).filter(Product.id == suggestion.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create reorder suggestion
    db_suggestion = ReorderSuggestion(
        product_id=suggestion.product_id,
        current_stock=suggestion.current_stock,
        recommended_quantity=suggestion.recommended_quantity,
        lead_time=suggestion.lead_time,
        confidence=suggestion.confidence,
        reasoning=suggestion.reasoning,
        trigger_reason=suggestion.trigger_reason
    )
    
    try:
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create reorder suggestion: {str(e)}")

@router.patch("/pricing/{suggestion_id}", response_model=PricingSuggestionResponse)
def update_pricing_suggestion(
    suggestion_id: int,
    update: PricingSuggestionUpdate,
    db: Session = Depends(get_db)
):
    """Update a pricing suggestion status (accept/reject)"""
    # Find pricing suggestion by ID
    db_suggestion = db.query(PricingSuggestion).filter(PricingSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        raise HTTPException(status_code=404, detail="Pricing suggestion not found")
    
    # Check if suggestion is already processed
    if db_suggestion.status != SuggestionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail=f"Suggestion already {db_suggestion.status.lower()}")
    
    # Update suggestion status
    db_suggestion.status = update.status
    
    # If accepted, update the product
    if update.status == SuggestionStatusEnum.ACCEPTED:
        db_product = db.query(Product).filter(Product.id == db_suggestion.product_id).first()
        if db_product:
            db_product.current_price = db_suggestion.recommended_price
            # Update product status if needed
            if db_product.stock_level == 0:
                db_product.status = ProductStatusEnum.OUT_OF_STOCK.value
            else:
                db_product.status = ProductStatusEnum.ACTIVE.value
    
    try:
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update pricing suggestion: {str(e)}")

@router.patch("/reorder/{suggestion_id}", response_model=ReorderSuggestionResponse)
def update_reorder_suggestion(
    suggestion_id: int,
    update: ReorderSuggestionUpdate,
    db: Session = Depends(get_db)
):
    """Update a reorder suggestion status (accept/reject)"""
    # Find reorder suggestion by ID
    db_suggestion = db.query(ReorderSuggestion).filter(ReorderSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        raise HTTPException(status_code=404, detail="Reorder suggestion not found")
    
    # Check if suggestion is already processed
    if db_suggestion.status != SuggestionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail=f"Suggestion already {db_suggestion.status.lower()}")
    
    # Update suggestion status
    db_suggestion.status = update.status
    
    # If accepted, update the product
    if update.status == SuggestionStatusEnum.ACCEPTED:
        db_product = db.query(Product).filter(Product.id == db_suggestion.product_id).first()
        if db_product:
            db_product.stock_level += db_suggestion.recommended_quantity
            # Update product status if needed
            if db_product.stock_level == 0:
                db_product.status = ProductStatusEnum.OUT_OF_STOCK.value
            else:
                db_product.status = ProductStatusEnum.ACTIVE.value
    
    try:
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update reorder suggestion: {str(e)}")