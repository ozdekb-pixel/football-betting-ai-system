"""
Football Betting AI System - User API
FastAPI application serving predictions and handling data ingestion
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_ingestion.database import get_db_session, init_db
from data_ingestion.schemas import BatchIngestRequest, IngestResponse
from data_ingestion.ingestion import DataIngestionService

# Initialize FastAPI app
app = FastAPI(
    title="Football Betting AI System",
    description="AI prediction engine for football betting intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Football Betting AI System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "data_ingestion": "/api/v1/data/ingest",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "football-betting-ai",
        "version": "1.0.0"
    }


@app.post(
    "/api/v1/data/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    tags=["Data Ingestion"]
)
async def ingest_data(
    request: BatchIngestRequest,
    db: Session = Depends(get_db_session)
):
    """
    Ingest match data from main application
    
    Accepts:
    - Historical matches with results
    - Upcoming fixtures without results
    - Team statistics
    - Betting odds
    
    Returns:
    - Processing statistics
    - Any errors encountered
    """
    try:
        service = DataIngestionService(db)
        response = service.ingest_batch(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": response.message,
                    "errors": response.errors
                }
            )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/v1/matches", tags=["Matches"])
async def get_matches(
    limit: int = 10,
    status: str = "scheduled",
    db: Session = Depends(get_db_session)
):
    """
    Get matches from database
    
    Query parameters:
    - limit: Number of matches to return (default: 10)
    - status: Match status filter (scheduled, completed, all)
    """
    from data_ingestion.models import Match, Team
    
    query = db.query(Match).join(
        Team, Match.home_team_id == Team.team_id
    )
    
    if status != "all":
        query = query.filter(Match.status == status)
    
    matches = query.order_by(Match.match_datetime).limit(limit).all()
    
    return {
        "total": len(matches),
        "matches": [
            {
                "match_id": m.match_id,
                "home_team": m.home_team.team_name,
                "away_team": m.away_team.team_name,
                "match_datetime": m.match_datetime.isoformat(),
                "league": m.league,
                "status": m.status
            }
            for m in matches
        ]
    }


@app.get("/api/v1/teams", tags=["Teams"])
async def get_teams(
    limit: int = 20,
    db: Session = Depends(get_db_session)
):
    """Get teams from database"""
    from data_ingestion.models import Team
    
    teams = db.query(Team).limit(limit).all()
    
    return {
        "total": len(teams),
        "teams": [
            {
                "team_id": t.team_id,
                "team_name": t.team_name,
                "league": t.league,
                "tier": t.tier
            }
            for t in teams
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "true").lower() == "true"
    )
