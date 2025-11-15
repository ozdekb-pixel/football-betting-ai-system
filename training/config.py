"""
Configuration for Training Module
Centralized configuration for data preparation, model training, and evaluation
"""

import os
from pathlib import Path
from typing import Dict, List

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = PROJECT_ROOT / "models"
BACKTESTING_DIR = PROJECT_ROOT / "backtesting"
BACKTESTING_RESULTS_DIR = BACKTESTING_DIR / "results"

# Create directories if they don't exist
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
BACKTESTING_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/football_betting_ai'
)

# Feature Engineering Configuration
LOOKBACK_WINDOWS = {
    'short': 5,   # Last 5 matches
    'medium': 10, # Last 10 matches
    'long': 20    # Last 20 matches (full season context)
}

# Minimum matches required for team statistics
MIN_MATCHES_FOR_STATS = 5

# Training Data Configuration
TRAINING_DATA_PATHS = {
    'goals': DATA_PROCESSED_DIR / "training_goals_over25.csv",
    'btts': DATA_PROCESSED_DIR / "training_btts.csv",
    'cards': DATA_PROCESSED_DIR / "training_cards.csv",
    'corners': DATA_PROCESSED_DIR / "training_corners.csv"
}

# Market Definitions
MARKETS = {
    'goals': {
        'name': 'Total Goals Over 2.5',
        'target_column': 'over_2_5',
        'odds_column': 'odds_over25',
        'threshold': 2.5
    },
    'btts': {
        'name': 'Both Teams To Score',
        'target_column': 'btts_yes',
        'odds_column': 'odds_btts_yes',
        'threshold': None
    },
    'cards': {
        'name': 'Total Cards Over 3.5',
        'target_column': 'cards_over_3_5',
        'odds_column': 'odds_cards_over35',
        'threshold': 3.5
    },
    'corners': {
        'name': 'Total Corners Over 9.5',
        'target_column': 'corners_over_9_5',
        'odds_column': 'odds_corners_over95',
        'threshold': 9.5
    }
}

# Model Training Configuration
MODEL_CONFIGS = {
    'logistic': {
        'name': 'Logistic Regression',
        'params': {
            'max_iter': 1000,
            'random_state': 42,
            'solver': 'lbfgs',
            'C': 1.0
        }
    },
    'xgboost': {
        'name': 'XGBoost',
        'params': {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss',
            'early_stopping_rounds': 20
        }
    },
    'lightgbm': {
        'name': 'LightGBM',
        'params': {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'verbose': -1
        }
    },
    'random_forest': {
        'name': 'Random Forest',
        'params': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'random_state': 42,
            'n_jobs': -1
        }
    }
}

# Default models to train for each market
DEFAULT_MODELS = ['logistic', 'xgboost', 'lightgbm']

# Ensemble Configuration
ENSEMBLE_WEIGHTS = {
    'logistic': 0.2,
    'xgboost': 0.5,
    'lightgbm': 0.3
}

# Calibration Configuration
CALIBRATION_METHOD = 'isotonic'  # 'isotonic' or 'sigmoid' (Platt scaling)

# Train/Validation/Test Split Configuration
TRAIN_SPLIT = 0.7  # 70% for training
VAL_SPLIT = 0.15   # 15% for validation
TEST_SPLIT = 0.15  # 15% for test

# Time-based split (prefer this over random split)
USE_TIME_BASED_SPLIT = True

# Backtesting Configuration
BACKTEST_CONFIG = {
    'initial_train_months': 12,  # Use 12 months for initial training
    'step_months': 1,            # Retrain every month
    'min_test_matches': 50,      # Minimum matches in test period
    'walk_forward': True         # Use walk-forward validation
}

# Retraining Configuration
RETRAIN_CONFIG = {
    'min_new_matches': 100,      # Minimum new matches before retraining
    'performance_threshold': {
        'log_loss': 0.65,        # Don't promote if log_loss > 0.65
        'brier_score': 0.25      # Don't promote if brier_score > 0.25
    },
    'version_increment': 'minor' # 'major', 'minor', or 'patch'
}

# Feature Groups (for feature importance analysis)
FEATURE_GROUPS = {
    'goals': [
        'home_goals_avg', 'away_goals_avg', 'home_goals_conceded_avg',
        'away_goals_conceded_avg', 'combined_goals_avg', 'expected_total_goals',
        'offensive_power', 'defensive_strength'
    ],
    'btts': [
        'home_btts_rate', 'away_btts_rate', 'combined_btts_rate',
        'both_teams_score_capability', 'both_teams_concede'
    ],
    'cards': [
        'home_cards_avg', 'away_cards_avg', 'combined_cards_avg',
        'expected_total_cards', 'high_card_rate'
    ],
    'corners': [
        'home_corners_avg', 'away_corners_avg', 'combined_corners_avg',
        'expected_total_corners', 'high_corner_rate', 'corner_dominance'
    ],
    'form': [
        'home_form_score', 'away_form_score', 'form_differential',
        'combined_form_score'
    ]
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Model Version Format
MODEL_VERSION_FORMAT = "v{major}.{minor}.{patch}"
INITIAL_VERSION = "v1.0.0"
