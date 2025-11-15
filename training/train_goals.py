"""
Train Goals Over 2.5 Model
Trains multiple models, creates ensemble, and applies calibration
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from training.config import (
    TRAINING_DATA_PATHS, MODEL_CONFIGS, DEFAULT_MODELS,
    ENSEMBLE_WEIGHTS, CALIBRATION_METHOD, USE_TIME_BASED_SPLIT,
    TRAIN_SPLIT, VAL_SPLIT
)
from training.utils import (
    fit_calibration_model, apply_calibration, calculate_metrics,
    ensemble_predictions, time_based_split, save_model_with_metadata,
    get_feature_importance, print_training_summary
)


def prepare_data(data_path: str) -> tuple:
    """
    Load and prepare data for training
    
    Args:
        data_path: Path to training CSV
        
    Returns:
        Tuple of (X_train, y_train, X_val, y_val, X_test, y_test, feature_columns)
    """
    print(f"📂 Loading data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Remove rows with missing target
    df = df.dropna(subset=['y'])
    
    # Define feature columns (exclude metadata and target)
    exclude_cols = ['match_id', 'date', 'league', 'home_team_id', 'away_team_id', 
                    'y', 'odds_over25']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Split data
    if USE_TIME_BASED_SPLIT and 'date' in df.columns:
        print("📅 Using time-based split")
        train_df, val_df, test_df = time_based_split(
            df, TRAIN_SPLIT, VAL_SPLIT, 'date'
        )
    else:
        print("🔀 Using random split")
        from sklearn.model_selection import train_test_split
        train_df, temp_df = train_test_split(df, train_size=TRAIN_SPLIT, random_state=42)
        val_df, test_df = train_test_split(
            temp_df, train_size=VAL_SPLIT/(VAL_SPLIT + (1-TRAIN_SPLIT-VAL_SPLIT)), 
            random_state=42
        )
    
    # Prepare features and targets
    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df['y'].astype(int)
    
    X_val = val_df[feature_cols].fillna(0)
    y_val = val_df['y'].astype(int)
    
    X_test = test_df[feature_cols].fillna(0)
    y_test = test_df['y'].astype(int)
    
    print(f"✅ Data prepared:")
    print(f"   Training:   {len(X_train):,} samples")
    print(f"   Validation: {len(X_val):,} samples")
    print(f"   Test:       {len(X_test):,} samples")
    print(f"   Features:   {len(feature_cols)}")
    
    # Check class distribution
    print(f"\n📊 Class distribution (training):")
    print(f"   Class 0: {(y_train == 0).sum():,} ({(y_train == 0).mean():.1%})")
    print(f"   Class 1: {(y_train == 1).sum():,} ({(y_train == 1).mean():.1%})")
    
    return X_train, y_train, X_val, y_val, X_test, y_test, feature_cols


def train_single_model(
    model_type: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> tuple:
    """
    Train a single model
    
    Args:
        model_type: Type of model to train
        X_train, y_train: Training data
        X_val, y_val: Validation data
        
    Returns:
        Tuple of (model, val_predictions, metrics)
    """
    print(f"\n🔄 Training {model_type.upper()} model...")
    
    config = MODEL_CONFIGS[model_type]
    params = config['params'].copy()
    
    # Initialize model
    if model_type == 'logistic':
        model = LogisticRegression(**params)
    elif model_type == 'xgboost':
        model = XGBClassifier(**params)
    elif model_type == 'lightgbm':
        model = LGBMClassifier(**params)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(**params)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train
    if model_type in ['xgboost', 'lightgbm']:
        # Use early stopping for gradient boosting
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
    else:
        model.fit(X_train, y_train)
    
    # Predict on validation set
    val_proba = model.predict_proba(X_val)[:, 1]
    val_pred = (val_proba >= 0.5).astype(int)
    
    # Calculate metrics
    metrics = calculate_metrics(y_val, val_proba, val_pred)
    
    print(f"✅ {model_type.upper()} trained:")
    print(f"   Log Loss:    {metrics['log_loss']:.4f}")
    print(f"   Brier Score: {metrics['brier_score']:.4f}")
    print(f"   Accuracy:    {metrics['accuracy']:.4f}")
    print(f"   AUC-ROC:     {metrics['auc_roc']:.4f}")
    
    return model, val_proba, metrics


def train_goals_model(data_path: Optional[str] = None) -> Dict:
    """
    Main training function for Goals Over 2.5 market
    
    Args:
        data_path: Path to training data (optional, uses default if not provided)
        
    Returns:
        Dictionary with training results
    """
    print("\n" + "=" * 60)
    print("TRAINING GOALS OVER 2.5 MODEL")
    print("=" * 60)
    
    # Use default path if not provided
    if data_path is None:
        data_path = str(TRAINING_DATA_PATHS['goals'])
    
    # Prepare data
    X_train, y_train, X_val, y_val, X_test, y_test, feature_cols = prepare_data(data_path)
    
    # Train multiple models
    models = {}
    val_predictions = {}
    all_metrics = {}
    
    for model_type in DEFAULT_MODELS:
        try:
            model, val_proba, metrics = train_single_model(
                model_type, X_train, y_train, X_val, y_val
            )
            models[model_type] = model
            val_predictions[model_type] = val_proba
            all_metrics[model_type] = metrics
        except Exception as e:
            print(f"❌ Error training {model_type}: {e}")
            continue
    
    if not models:
        print("❌ No models were successfully trained!")
        return {}
    
    # Create ensemble
    print("\n🔄 Creating ensemble...")
    ensemble_proba = ensemble_predictions(val_predictions, ENSEMBLE_WEIGHTS)
    ensemble_metrics = calculate_metrics(y_val, ensemble_proba)
    
    print(f"✅ Ensemble performance:")
    print(f"   Log Loss:    {ensemble_metrics['log_loss']:.4f}")
    print(f"   Brier Score: {ensemble_metrics['brier_score']:.4f}")
    print(f"   Accuracy:    {ensemble_metrics['accuracy']:.4f}")
    print(f"   AUC-ROC:     {ensemble_metrics['auc_roc']:.4f}")
    
    # Apply calibration
    print(f"\n🔄 Applying {CALIBRATION_METHOD} calibration...")
    calibration_model = fit_calibration_model(
        ensemble_proba, y_val.values, method=CALIBRATION_METHOD
    )
    calibrated_proba = apply_calibration(
        calibration_model, ensemble_proba, method=CALIBRATION_METHOD
    )
    calibrated_metrics = calculate_metrics(y_val, calibrated_proba)
    
    print(f"✅ Calibrated ensemble performance:")
    print(f"   Log Loss:    {calibrated_metrics['log_loss']:.4f}")
    print(f"   Brier Score: {calibrated_metrics['brier_score']:.4f}")
    print(f"   Accuracy:    {calibrated_metrics['accuracy']:.4f}")
    print(f"   AUC-ROC:     {calibrated_metrics['auc_roc']:.4f}")
    
    # Test set evaluation
    print("\n🔄 Evaluating on test set...")
    test_predictions = {}
    for model_type, model in models.items():
        test_predictions[model_type] = model.predict_proba(X_test)[:, 1]
    
    test_ensemble = ensemble_predictions(test_predictions, ENSEMBLE_WEIGHTS)
    test_calibrated = apply_calibration(
        calibration_model, test_ensemble, method=CALIBRATION_METHOD
    )
    test_metrics = calculate_metrics(y_test, test_calibrated)
    
    print(f"✅ Test set performance (calibrated ensemble):")
    print(f"   Log Loss:    {test_metrics['log_loss']:.4f}")
    print(f"   Brier Score: {test_metrics['brier_score']:.4f}")
    print(f"   Accuracy:    {test_metrics['accuracy']:.4f}")
    print(f"   AUC-ROC:     {test_metrics['auc_roc']:.4f}")
    
    # Save models
    print("\n💾 Saving models...")
    for model_type, model in models.items():
        save_model_with_metadata(
            model=model,
            market='goals',
            metrics=all_metrics[model_type],
            feature_columns=feature_cols,
            model_type=model_type,
            train_start_date=None,
            train_end_date=None,
            additional_info={
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'test_samples': len(X_test)
            }
        )
    
    # Save ensemble metadata
    ensemble_info = {
        'market': 'goals',
        'model_type': 'ensemble',
        'version': 'v1.0.0',
        'base_models': list(models.keys()),
        'weights': ENSEMBLE_WEIGHTS,
        'calibration_method': CALIBRATION_METHOD,
        'metrics': {
            'validation': calibrated_metrics,
            'test': test_metrics
        },
        'feature_columns': feature_cols
    }
    
    import json
    from training.config import MODELS_DIR
    ensemble_path = MODELS_DIR / 'goals' / 'ensemble_metadata.json'
    with open(ensemble_path, 'w') as f:
        json.dump(ensemble_info, f, indent=2)
    
    # Save calibration model
    import pickle
    calib_path = MODELS_DIR / 'goals' / 'ensemble_calibration.pkl'
    with open(calib_path, 'wb') as f:
        pickle.dump(calibration_model, f)
    
    print(f"💾 Saved ensemble metadata to {ensemble_path}")
    print(f"💾 Saved calibration model to {calib_path}")
    
    # Feature importance (for best tree-based model)
    best_tree_model = None
    best_tree_type = None
    for model_type in ['xgboost', 'lightgbm', 'random_forest']:
        if model_type in models:
            best_tree_model = models[model_type]
            best_tree_type = model_type
            break
    
    if best_tree_model:
        print(f"\n📊 Top 10 features ({best_tree_type}):")
        importance_df = get_feature_importance(best_tree_model, feature_cols, top_n=10)
        for idx, row in importance_df.iterrows():
            print(f"   {row['feature']:30s}: {row['importance']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ GOALS MODEL TRAINING COMPLETE")
    print("=" * 60)
    
    return {
        'models': models,
        'ensemble_metrics': calibrated_metrics,
        'test_metrics': test_metrics,
        'calibration_model': calibration_model,
        'feature_columns': feature_cols
    }


if __name__ == "__main__":
    from training.config import Optional
    train_goals_model()
