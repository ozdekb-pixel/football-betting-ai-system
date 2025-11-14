# Model Training Guide

## 🤖 Automated Training (Recommended)

Your repository now has automated model training via GitHub Actions!

### How It Works

The workflow automatically trains models when:
1. **Manual trigger** - You click "Run workflow" in GitHub Actions
2. **Data changes** - When you update test data files
3. **Code changes** - When you modify training scripts
4. **Weekly schedule** - Every Sunday at 2 AM UTC

### Manual Trigger (Do This Now!)

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Train AI Models** workflow
4. Click **Run workflow** dropdown
5. Click green **Run workflow** button

The workflow will:
- ✅ Install all dependencies
- ✅ Train 4 models (goals, cards, corners, btts)
- ✅ Generate performance metrics
- ✅ Commit models back to repo
- ✅ Display training summary

### View Results

After the workflow completes:
- Check the **Summary** tab for metrics
- Models will be in `smart-bets-ai/models/`
- New commit with trained models

---

## 💻 Local Training (Alternative)

If you prefer to train locally:

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Train Models
```bash
# From project root
python smart-bets-ai/train.py
```

### What Happens
1. Loads data from `test-data/historical_matches_sample.json`
2. Engineers features for each market
3. Trains 4 XGBoost models
4. Saves models to `smart-bets-ai/models/`
5. Displays performance metrics

### Expected Output
```
============================================================
SMART BETS AI - MODEL TRAINING
============================================================
✅ Loaded 50 matches from test-data/historical_matches_sample.json

🔄 Training GOALS model...
✅ GOALS Model Performance:
   Accuracy: 0.6500
   Log Loss: 0.6234
   AUC-ROC: 0.6789

🔄 Training CARDS model...
✅ CARDS Model Performance:
   Accuracy: 0.6200
   Log Loss: 0.6456
   AUC-ROC: 0.6543

🔄 Training CORNERS model...
✅ CORNERS Model Performance:
   Accuracy: 0.6400
   Log Loss: 0.6321
   AUC-ROC: 0.6678

🔄 Training BTTS model...
✅ BTTS Model Performance:
   Accuracy: 0.6300
   Log Loss: 0.6389
   AUC-ROC: 0.6612

💾 Saved goals model to models/goals_model.pkl
💾 Saved cards model to models/cards_model.pkl
💾 Saved corners model to models/corners_model.pkl
💾 Saved btts model to models/btts_model.pkl
💾 Saved feature engineer to models/feature_engineer.pkl
💾 Saved metadata to models/metadata.json

============================================================
✅ TRAINING COMPLETE
============================================================
```

---

## 📊 Understanding Metrics

### Accuracy
- **What:** Percentage of correct predictions
- **Target:** >60%
- **Interpretation:** Higher is better

### Log Loss
- **What:** Measures probability calibration
- **Target:** <0.65
- **Interpretation:** Lower is better

### AUC-ROC
- **What:** Model's discrimination ability
- **Target:** >0.65
- **Interpretation:** Higher is better (0.5 = random, 1.0 = perfect)

---

## 🔄 Retraining Models

### When to Retrain
- ✅ After adding more historical data
- ✅ Weekly (automated via schedule)
- ✅ When model performance degrades
- ✅ After updating feature engineering

### How to Retrain
**Automated:** Just push new data to `test-data/` folder
**Manual:** Run the workflow or execute locally

---

## 📁 Generated Files

After training, you'll have:

```
smart-bets-ai/models/
├── goals_model.pkl          # Goals O/U 2.5 model
├── cards_model.pkl          # Cards O/U 3.5 model
├── corners_model.pkl        # Corners O/U 9.5 model
├── btts_model.pkl           # BTTS Yes/No model
├── feature_engineer.pkl     # Feature transformation pipeline
└── metadata.json            # Training metrics and info
```

---

## 🚨 Troubleshooting

### "No module named 'smart_bets_ai'"
**Solution:** Run from project root, not from `smart-bets-ai/` directory

### "FileNotFoundError: historical_matches_sample.json"
**Solution:** Ensure you're in project root and file exists in `test-data/`

### Low Accuracy (<50%)
**Cause:** Sample data is limited (5-50 matches)
**Solution:** 
- This is expected with small datasets
- Models will improve with more data (300+ matches)
- For now, focus on structure working correctly

### Models Not Loading in Predictions
**Solution:** 
1. Verify models exist: `ls smart-bets-ai/models/`
2. Check file permissions
3. Retrain if files are corrupted

---

## 🎯 Next Steps

After training models:

1. **Test Predictions**
   ```bash
   python smart-bets-ai/predict.py
   ```

2. **Start API Server**
   ```bash
   cd user-api
   python main.py
   ```

3. **Make API Request**
   ```bash
   curl -X POST http://localhost:8000/api/v1/predictions/smart-bets \
     -H "Content-Type: application/json" \
     -d @test-data/upcoming_fixtures_200.json
   ```

4. **Move to Phase 3: Golden Bets AI**
   - Implement 85%+ confidence filtering
   - Add ensemble agreement metrics
   - Build daily picks endpoint

---

## 📖 Additional Resources

- **Smart Bets README:** `smart-bets-ai/README.md`
- **Feature Engineering:** `smart-bets-ai/features.py`
- **Training Script:** `smart-bets-ai/train.py`
- **Prediction Service:** `smart-bets-ai/predict.py`
- **Test Data Guide:** `test-data/README.md`

---

## 💡 Pro Tips

1. **Start with sample data** - Don't worry about volume initially
2. **Monitor metrics** - Track accuracy/log loss over time
3. **Retrain regularly** - Weekly retraining keeps models fresh
4. **Version models** - Metadata includes training timestamp
5. **Test predictions** - Always verify output before deploying

---

**Ready to train? Go to Actions → Train AI Models → Run workflow!** 🚀
