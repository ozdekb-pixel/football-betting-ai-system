# ⚽ Football Betting AI System

> **🤖 FULLY AUTOMATED** - Models train, test, and deploy automatically  
> **✅ PRODUCTION READY** - Live on Railway with zero manual intervention  
> **📊 SELF-MAINTAINING** - Tests run every 6 hours, models retrain weekly  
> **🚀 NO BABYSITTING** - System handles everything

---

## 🎯 Quick Links

- **Live API:** https://football-betting-ai-system-production.up.railway.app
- **Workflows:** [GitHub Actions](https://github.com/dannythehat/football-betting-ai-system/actions)
- **Execution Summary:** [EXECUTION_SUMMARY.md](EXECUTION_SUMMARY.md)
- **API Docs:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **System Status:** [SYSTEM_STATUS.md](SYSTEM_STATUS.md)

---

## What This System Does

AI-powered betting intelligence for **4 specific markets:**
1. **Goals:** Over/Under 2.5
2. **Cards:** Over/Under 3.5
3. **Corners:** Over/Under 9.5
4. **BTTS:** Both Teams To Score (Yes/No)

### Four Betting Intelligence Features

#### 1. Smart Bets AI ✅
**Best single bet per match**
- Analyzes all 4 markets
- Selects highest confidence prediction
- One recommendation per fixture

#### 2. Golden Bets AI ✅
**Daily premium picks (1-3 bets)**
- 85%+ confidence threshold
- Safety-focused selections
- Top 1-3 safest bets of the day

#### 3. Value Bets AI ✅
**Profit-focused picks (Top 3)**
- Positive expected value only
- Calculates EV for each bet
- Ranked by profit potential

#### 4. Custom Analysis ✅
**Educational bet analysis**
- User selects fixture + market
- Detailed AI reasoning
- Risk assessment included

---

## 🤖 Automation Status

### Model Training
- **Frequency:** Weekly (Sundays 2 AM UTC) + on-demand
- **Workflow:** `.github/workflows/train-models.yml`
- **Status:** ✅ Active

### Testing
- **Frequency:** Every 6 hours + on every push
- **Workflow:** `.github/workflows/full-test-deploy.yml`
- **Status:** ✅ Running

### Deployment
- **Platform:** Railway
- **Trigger:** Auto-deploy on push to main
- **Status:** ✅ Live

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| **Smart Bets AI** | ✅ Working | Automated testing |
| **Golden Bets AI** | ✅ Working | 85%+ confidence |
| **Value Bets AI** | ✅ Working | Positive EV |
| **Custom Analysis** | ✅ Working | Educational |
| **Model Training** | ✅ Automated | Weekly schedule |
| **Testing Suite** | ✅ Running | Every 6 hours |
| **Production API** | ✅ Live | Railway deployment |

---

## 🚀 Quick Start

### Option 1: Use the Live API
```bash
# Health check
curl https://football-betting-ai-system-production.up.railway.app/health

# Get predictions
curl -X POST https://football-betting-ai-system-production.up.railway.app/api/v1/predictions/smart-bets \
  -H "Content-Type: application/json" \
  -d '{"matches": [...]}'
```

### Option 2: Monitor Automation
```bash
# View workflow runs
https://github.com/dannythehat/football-betting-ai-system/actions

# Check test results
cat test-results/TEST_REPORT.md

# View model metrics
cat smart-bets-ai/models/metadata.json
```

### Option 3: Local Development
```bash
# Clone and install
git clone https://github.com/dannythehat/football-betting-ai-system.git
cd football-betting-ai-system
pip install -r requirements.txt

# Train models
python smart-bets-ai/train.py

# Test components
python smart-bets-ai/predict.py
python golden-bets-ai/test_filter.py
python value-bets-ai/predict.py
python custom-analysis/test_analyzer.py

# Start API
cd user-api && python main.py
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [EXECUTION_SUMMARY.md](EXECUTION_SUMMARY.md) | What was built and how it works |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide and monitoring |
| [TESTING_VALIDATION.md](TESTING_VALIDATION.md) | Testing procedures |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [SYSTEM_STATUS.md](SYSTEM_STATUS.md) | Real-time system health |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |

---

## 🔍 How It Works

### Automated Workflow

1. **Model Training (Weekly)**
   - Trains 4 AI models (Goals, Cards, Corners, BTTS)
   - Validates performance
   - Commits models to repo
   - Logs metrics

2. **Testing (Every 6 Hours)**
   - Tests all 4 AI components
   - Validates predictions
   - Commits results to repo
   - Updates documentation

3. **Deployment (On Push)**
   - Railway auto-deploys
   - Zero downtime
   - Instant updates

### Manual Triggers (Optional)

```bash
# Trigger model training
gh workflow run train-models.yml

# Trigger full test suite
gh workflow run full-test-deploy.yml
```

---

## 🎯 API Endpoints

**Base URL:** `https://football-betting-ai-system-production.up.railway.app`

- `GET /health` - Health check
- `POST /api/v1/predictions/smart-bets` - Best bet per match
- `POST /api/v1/predictions/golden-bets` - Daily premium picks
- `POST /api/v1/predictions/value-bets` - Profit-focused picks
- `POST /api/v1/predictions/custom-analysis` - Educational analysis

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details.

---

## 🛠️ Tech Stack

- **ML:** XGBoost, LightGBM, scikit-learn
- **API:** FastAPI, Uvicorn
- **Database:** PostgreSQL
- **Cache:** Redis
- **Deployment:** Railway
- **CI/CD:** GitHub Actions
- **Testing:** pytest, automated workflows

---

## 📈 What Happens Automatically

- ✅ Models train weekly
- ✅ Tests run every 6 hours
- ✅ Results committed to repo
- ✅ Deployment on every push
- ✅ API stays live 24/7
- ✅ Metrics tracked continuously

**No manual intervention required.**

---

## ✅ Success Criteria

- [x] Models train automatically
- [x] Tests run without intervention
- [x] System deployed to production
- [x] API endpoints functional
- [x] Documentation complete
- [x] Monitoring in place
- [x] Zero babysitting required

**All criteria met ✅**

---

## 🎉 Bottom Line

**This system:**
- Trains itself
- Tests itself
- Deploys itself
- Documents itself
- Maintains itself

**Your job:**
- Monitor occasionally
- Use the API
- Enjoy your holiday

**System's job:**
- Everything else

---

## 📞 Support

Check these in order:
1. [Workflow runs](https://github.com/dannythehat/football-betting-ai-system/actions)
2. [Test results](test-results/TEST_REPORT.md)
3. [System status](SYSTEM_STATUS.md)
4. [Documentation](EXECUTION_SUMMARY.md)

---

**Built by:** Bhindi AI  
**Status:** Production Ready ✅  
**Last Updated:** Auto-generated on every commit
