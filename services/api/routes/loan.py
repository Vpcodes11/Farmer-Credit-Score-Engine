"""
Loan eligibility routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Farmer, Score
from schemas import LoanQuoteRequest, LoanQuoteResponse, EMIPlan
from auth import get_current_active_user

router = APIRouter(prefix="/loan", tags=["Loan"])

# Crop cycle mapping (months)
CROP_CYCLES = {
    'rice': 4,
    'wheat': 5,
    'cotton': 6,
    'maize': 4
}

def calculate_max_loan(score: float, land_area: float) -> float:
    """Calculate maximum loan amount based on score and land area"""
    # Base amount per hectare
    base_per_hectare = 50000  # ₹50,000 per hectare
    
    # Score multiplier (0.4 to 1.2)
    score_multiplier = 0.4 + (score / 100) * 0.8
    
    max_loan = land_area * base_per_hectare * score_multiplier
    
    return round(max_loan, 2)

def generate_emi_plans(
    loan_amount: float,
    score: float,
    crop_cycle_months: int
) -> List[EMIPlan]:
    """Generate flexible EMI plans based on crop cycle"""
    plans = []
    
    # Base interest rate (8% to 12% based on score)
    base_rate = 12 - (score / 100) * 4
    
    # Plan 1: Crop cycle aligned (bullet payment)
    plans.append(EMIPlan(
        emi_amount=round(loan_amount * (1 + base_rate/100 * crop_cycle_months/12), 2),
        duration_months=crop_cycle_months,
        interest_rate=round(base_rate, 2),
        total_repayment=round(loan_amount * (1 + base_rate/100 * crop_cycle_months/12), 2)
    ))
    
    # Plan 2: 12 months
    monthly_rate = base_rate / 12 / 100
    n = 12
    emi_12 = loan_amount * monthly_rate * (1 + monthly_rate)**n / ((1 + monthly_rate)**n - 1)
    plans.append(EMIPlan(
        emi_amount=round(emi_12, 2),
        duration_months=12,
        interest_rate=round(base_rate, 2),
        total_repayment=round(emi_12 * 12, 2)
    ))
    
    # Plan 3: 24 months (if score > 50)
    if score > 50:
        n = 24
        emi_24 = loan_amount * monthly_rate * (1 + monthly_rate)**n / ((1 + monthly_rate)**n - 1)
        plans.append(EMIPlan(
            emi_amount=round(emi_24, 2),
            duration_months=24,
            interest_rate=round(base_rate, 2),
            total_repayment=round(emi_24 * 24, 2)
        ))
    
    return plans

@router.post("/quote", response_model=LoanQuoteResponse)
def get_loan_quote(
    request: LoanQuoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get loan eligibility and EMI quote for a farmer
    
    Args:
        request: Loan quote request
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Loan eligibility with EMI plans
    """
    # Get farmer
    farmer = db.query(Farmer).filter(Farmer.farmer_id == request.farmer_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer {request.farmer_id} not found"
        )
    
    # Get latest score
    latest_score = db.query(Score).filter(
        Score.farmer_id == farmer.id
    ).order_by(Score.computed_at.desc()).first()
    
    if not latest_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No credit score found. Please compute score first."
        )
    
    score_value = latest_score.score
    land_area = farmer.land_area or 2.0
    crop_type = farmer.crop_type or 'rice'
    
    # Calculate eligibility
    eligible = score_value >= 30  # Minimum score for eligibility
    max_loan = calculate_max_loan(score_value, land_area)
    recommended = max_loan * 0.8  # Recommend 80% of max
    
    # Get crop cycle
    crop_cycle_months = CROP_CYCLES.get(crop_type, 4)
    
    # Generate EMI plans
    loan_amount = request.requested_amount if request.requested_amount else recommended
    loan_amount = min(loan_amount, max_loan)  # Cap at max
    
    emi_plans = generate_emi_plans(loan_amount, score_value, crop_cycle_months)
    
    # Generate remarks
    if score_value >= 70:
        remarks = "Excellent credit profile. Eligible for premium rates."
    elif score_value >= 50:
        remarks = "Good credit profile. Standard rates applicable."
    elif score_value >= 30:
        remarks = "Fair credit profile. Higher interest rates may apply."
    else:
        remarks = "Credit score below threshold. Loan not recommended."
    
    return LoanQuoteResponse(
        farmer_id=request.farmer_id,
        credit_score=score_value,
        eligible=eligible,
        max_loan_amount=max_loan,
        recommended_amount=recommended,
        emi_plans=emi_plans,
        crop_cycle_months=crop_cycle_months,
        remarks=remarks
    )
