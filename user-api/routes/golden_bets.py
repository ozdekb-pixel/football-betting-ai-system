"""
Golden Bets API Routes
Endpoint for retrieving daily 1-3 highest confidence picks
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from golden_bets_ai import GoldenBetsPredictor, GoldenBetsFilter

router = APIRouter(prefix="/api/v1/predictions", tags=["Golden Bets"])

@router.post("/golden-bets")
async def get_golden_bets(request: Dict[str, Any]):
    """
    Get Golden Bets predictions (1-3 daily picks with 85%+ confidence)
    
    Request body:
    {
        "matches": [
            {
                "match_id": "12345",
                "datetime": "2025-11-15T14:00:00Z",
                "home_team": "Team A",
                "away_team": "Team B",
                "stats": {...},
                "odds": {...}
            }
        ]
    }
    
    Response:
    {
        "golden_bets": [...],
        "total_candidates": 15,
        "selected_count": 3,
        "timestamp": "2025-11-15T03:44:33Z"
    }
    """
    try:
        matches = request.get('matches', [])
        
        if not matches:
            raise HTTPException(status_code=400, detail="No matches provided")
        
        # Use predictor to get Golden Bets
        predictor = GoldenBetsPredictor()
        golden_bets = predictor.predict(matches)
        
        # Get total candidates from Smart Bets
        smart_predictions = predictor.smart_bets_predictor.predict(matches)
        
        return {
            "golden_bets": golden_bets,
            "total_candidates": len(smart_predictions),
            "selected_count": len(golden_bets),
            "timestamp": request.get('timestamp', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Golden Bets prediction failed: {str(e)}")

@router.get("/golden-bets/config")
async def get_golden_bets_config():
    """
    Get current Golden Bets configuration
    
    Response:
    {
        "confidence_threshold": 0.85,
        "min_ensemble_agreement": 0.90,
        "max_daily_picks": 3
    }
    """
    filter = GoldenBetsFilter()
    
    return {
        "confidence_threshold": filter.confidence_threshold,
        "min_ensemble_agreement": filter.min_agreement,
        "max_daily_picks": filter.max_picks,
        "probability_weight": 0.7,
        "agreement_weight": 0.3
    }
