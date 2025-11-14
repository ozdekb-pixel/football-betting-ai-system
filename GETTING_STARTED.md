# Getting Started - Football Betting AI System

## 🚀 Quick Start (3 Steps)

### Option 1: Docker (Recommended - Easiest)

```bash
# 1. Clone repository
git clone https://github.com/dannythehat/football-betting-ai-system.git
cd football-betting-ai-system

# 2. Start everything with Docker
docker-compose up -d

# 3. Generate and load test data
cd test-data
python3 generate_test_data.py
cd ..
python3 scripts/load_test_data.py

# ✅ Done! API running at http://localhost:8000
```

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone https://github.com/dannythehat/football-betting-ai-system.git
cd football-betting-ai-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup PostgreSQL and Redis
# Install PostgreSQL 15+ and Redis 7+
# Create database: createdb football_betting_ai

# 5. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 6. Generate test data
cd test-data
python3 generate_test_data.py
cd ..

# 7. Load test data
python3 scripts/load_test_data.py

# 8. Start API
uvicorn user-api.main:app --reload

# ✅ Done! API running at http://localhost:8000
```

---

## 📊 What Just Happened?

You now have:

✅ **PostgreSQL database** with complete schema  
✅ **Redis cache** for fast predictions  
✅ **FastAPI application** running  
✅ **Test data loaded:**
   - 300 historical matches (if generated)
   - 200 upcoming fixtures (if generated)
   - 400 teams across 20 leagues

---

## 🧪 Test Your Setup

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "football-betting-ai",
  "version": "1.0.0"
}
```

### 2. View API Documentation
Open browser: **http://localhost:8000/docs**

### 3. Get Matches
```bash
curl http://localhost:8000/api/v1/matches?limit=5
```

### 4. Get Teams
```bash
curl http://localhost:8000/api/v1/teams?limit=10
```

### 5. Test Data Ingestion
```bash
curl -X POST http://localhost:8000/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d @test-data/historical_matches_sample.json
```

---

## 📁 Project Structure

```
football-betting-ai-system/
├── data-ingestion/          # Data ingestion module ✅ COMPLETE
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic validation schemas
│   ├── database.py         # Database connection
│   ├── ingestion.py        # Core ingestion logic
│   └── __init__.py
├── user-api/               # FastAPI application ✅ COMPLETE
│   └── main.py            # API endpoints
├── smart-bets-ai/         # Smart Bets AI module (TODO)
├── golden-bets-ai/        # Golden Bets AI module (TODO)
├── value-bets-ai/         # Value Bets AI module (TODO)
├── odds-updater/          # Odds processing (TODO)
├── summary-generator/     # Explanation generator (TODO)
├── test-data/             # Test data ✅ COMPLETE
│   ├── generate_test_data.py
│   ├── teams.json
│   └── schema.sql
├── scripts/               # Utility scripts ✅ COMPLETE
│   └── load_test_data.py
├── requirements.txt       # Python dependencies ✅ COMPLETE
├── docker-compose.yml     # Docker setup ✅ COMPLETE
├── Dockerfile            # Container config ✅ COMPLETE
└── .env.example          # Environment template ✅ COMPLETE
```

---

## 🎯 What's Working Now

### ✅ Phase 1: Foundation (COMPLETE)

1. **Database Schema** - PostgreSQL with all tables
2. **Data Ingestion** - Accepts match data via API
3. **Data Validation** - Pydantic schemas validate input
4. **API Endpoints** - FastAPI serving data
5. **Docker Setup** - One-command deployment
6. **Test Data** - 300 matches + 200 fixtures

### 🔄 Next Steps (Phase 2)

1. **Smart Bets AI** - Build prediction model
2. **Feature Engineering** - Extract features from match data
3. **Model Training** - Train XGBoost on historical data
4. **Prediction Endpoint** - Serve predictions via API

---

## 🛠️ Development Workflow

### Daily Development

```bash
# Start services
docker-compose up -d

# Watch logs
docker-compose logs -f api

# Run tests (when added)
pytest

# Stop services
docker-compose down
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it football_betting_db psql -U football_ai -d football_betting_ai

# View tables
\dt

# Query matches
SELECT match_id, home_team_id, away_team_id, match_datetime FROM matches LIMIT 5;

# Exit
\q
```

### Redis Management

```bash
# Access Redis
docker exec -it football_betting_redis redis-cli

# Check keys
KEYS *

# Exit
exit
```

---

## 📝 Environment Variables

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://football_ai:football_ai_password@localhost:5432/football_betting_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Model
MODEL_VERSION=v1.0.0
CONFIDENCE_THRESHOLD=0.85
VALUE_THRESHOLD=0.10
```

---

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Import Errors
```bash
# Ensure you're in project root
pwd

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Next Documentation

- **ROADMAP.md** - Full implementation plan
- **FEATURES.md** - Detailed feature descriptions
- **SCOPE.md** - Technical specifications
- **README.md** - Project overview

---

## 🎉 You're Ready!

Your foundation is solid. The data ingestion module is complete and working.

**Next milestone:** Build the Smart Bets AI prediction model.

Questions? Check the docs or raise an issue on GitHub.

**Happy coding! 🚀**
