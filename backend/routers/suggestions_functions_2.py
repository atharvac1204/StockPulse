@router.patch("/pricing/{suggestion_id}", response_model=PricingSuggestionResponse)
def update_pricing_suggestion(
    suggestion_id: int,
    suggestion_update: PricingSuggestionUpdate,
    db: Session = Depends(get_db)
):
    """Update a pricing suggestion (accept/reject)"""
    # Get the suggestion
    db_suggestion = db.query(PricingSuggestion).filter(PricingSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        raise HTTPException(status_code=404, detail="Pricing suggestion not found")
    
    # Check if already processed
    if db_suggestion.status != SuggestionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Suggestion has already been processed")
    
    # Get the associated product
    db_product = db.query(Product).filter(Product.id == db_suggestion.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Associated product not found")
    
    # Update suggestion status
    db_suggestion.status = suggestion_update.status
    
    # If accepted, update product price
    if suggestion_update.status == SuggestionStatusEnum.ACCEPTED:
        db_product.current_price = db_suggestion.recommended_price
    
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
    suggestion_update: ReorderSuggestionUpdate,
    db: Session = Depends(get_db)
):
    """Update a reorder suggestion (accept/reject)"""
    # Get the suggestion
    db_suggestion = db.query(ReorderSuggestion).filter(ReorderSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        raise HTTPException(status_code=404, detail="Reorder suggestion not found")
    
    # Check if already processed
    if db_suggestion.status != SuggestionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Suggestion has already been processed")
    
    # Get the associated product
    db_product = db.query(Product).filter(Product.id == db_suggestion.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Associated product not found")
    
    # Update suggestion status
    db_suggestion.status = suggestion_update.status
    
    # If accepted, update product stock
    if suggestion_update.status == SuggestionStatusEnum.ACCEPTED:
        db_product.stock_level += db_suggestion.recommended_quantity
        # Update product status based on new stock level
        if db_product.stock_level > 0:
            db_product.status = "ACTIVE"
    
    try:
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update reorder suggestion: {str(e)}")