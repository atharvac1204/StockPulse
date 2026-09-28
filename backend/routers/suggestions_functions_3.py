@router.get("/pricing", response_model=List[PricingSuggestionResponse])
def get_pricing_suggestions(
    status: Optional[SuggestionStatusEnum] = None,
    trigger_reason: Optional[TriggerReasonEnum] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get pricing suggestions with optional filtering"""
    query = db.query(PricingSuggestion)
    
    if status:
        query = query.filter(PricingSuggestion.status == status)
    
    if trigger_reason:
        query = query.filter(PricingSuggestion.trigger_reason == trigger_reason)
    
    if product_id:
        query = query.filter(PricingSuggestion.product_id == product_id)
    
    return query.all()

@router.get("/reorder", response_model=List[ReorderSuggestionResponse])
def get_reorder_suggestions(
    status: Optional[SuggestionStatusEnum] = None,
    trigger_reason: Optional[TriggerReasonEnum] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get reorder suggestions with optional filtering"""
    query = db.query(ReorderSuggestion)
    
    if status:
        query = query.filter(ReorderSuggestion.status == status)
    
    if trigger_reason:
        query = query.filter(ReorderSuggestion.trigger_reason == trigger_reason)
    
    if product_id:
        query = query.filter(ReorderSuggestion.product_id == product_id)
    
    return query.all()