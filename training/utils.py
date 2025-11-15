"""
Training Utilities
Shared helper functions for model training, calibration, and evaluation
"""

import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score, accuracy_score
import warnings
warnings.filterwarnings('ignore')

from training.config import MODELS_DIR, MODEL_VERSION_FORMAT, INITIAL_VERSION


def fit_calibration_model(
    raw_probs: np.ndarray, 
    y_true: np.ndarray,
    method: str = 'isotonic'
) -> Any:
    """
    Train a calibration model to improve probability estimates
    
    Args:
        raw_probs: Raw probability predictions from model
        y_true: True binary labels
        method: 'isotonic' for isotonic regression or 'sigmoid' for Platt scaling
        
    Returns:
        Trained calibration model
    """
    if method == 'isotonic':
        calibrator = IsotonicRegression(out_of_bounds='clip')
        calibrator.fit(raw_probs, y_true)
    elif method == 'sigmoid':
        # Platt scaling using logistic regression
        calibrator = LogisticRegression()
        calibrator.fit(raw_probs.reshape(-1, 1), y_true)
    else:
        raise ValueError(f"Unknown calibration method: {method}")
    
    return calibrator


def apply_calibration(
    calibration_model: Any, 
    raw_probs: np.ndarray,
    method: str = 'isotonic'
) -> np.ndarray:
    """
    Apply trained calibration model to raw probabilities
    
    Args:
        calibration_model: Trained calibration model
        raw_probs: Raw probability predictions
        method: Calibration method used ('isotonic' or 'sigmoid')
        
    Returns:
        Calibrated probabilities
    """
    if method == 'isotonic':
        return calibration_model.predict(raw_probs)
    elif method == 'sigmoid':
        return calibration_model.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
    else:
        raise ValueError(f"Unknown calibration method: {method}")


def calculate_metrics(
    y_true: np.ndarray, 
    y_pred_proba: np.ndarray,
    y_pred_binary: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics
    
    Args:
        y_true: True binary labels
        y_pred_proba: Predicted probabilities
        y_pred_binary: Predicted binary labels (optional, will be computed if not provided)
        
    Returns:
        Dictionary with metric names and values
    """
    if y_pred_binary is None:
        y_pred_binary = (y_pred_proba >= 0.5).astype(int)
    
    metrics = {
        'log_loss': float(log_loss(y_true, y_pred_proba)),
        'brier_score': float(brier_score_loss(y_true, y_pred_proba)),
        'accuracy': float(accuracy_score(y_true, y_pred_binary))
    }
    
    # Add AUC-ROC if possible
    try:
        metrics['auc_roc'] = float(roc_auc_score(y_true, y_pred_proba))
    except:
        metrics['auc_roc'] = 0.0
    
    return metrics


def calculate_calibration_curve(
    y_true: np.ndarray, 
    y_pred_proba: np.ndarray,
    n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate calibration curve (reliability diagram data)
    
    Args:
        y_true: True binary labels
        y_pred_proba: Predicted probabilities
        n_bins: Number of bins for calibration curve
        
    Returns:
        Tuple of (mean_predicted_prob, fraction_of_positives) for each bin
    """
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred_proba, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    mean_predicted = []
    fraction_positive = []
    
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            mean_predicted.append(y_pred_proba[mask].mean())
            fraction_positive.append(y_true[mask].mean())
        else:
            mean_predicted.append(bins[i] + (bins[i+1] - bins[i]) / 2)
            fraction_positive.append(np.nan)
    
    return np.array(mean_predicted), np.array(fraction_positive)


def ensemble_predictions(
    predictions_dict: Dict[str, np.ndarray],
    weights: Optional[Dict[str, float]] = None
) -> np.ndarray:
    """
    Combine predictions from multiple models using weighted average
    
    Args:
        predictions_dict: Dictionary mapping model names to their predictions
        weights: Dictionary mapping model names to their weights (optional)
        
    Returns:
        Ensemble predictions
    """
    if weights is None:
        # Equal weights
        weights = {name: 1.0 / len(predictions_dict) for name in predictions_dict}
    
    # Normalize weights
    total_weight = sum(weights.values())
    weights = {name: w / total_weight for name, w in weights.items()}
    
    # Weighted average
    ensemble = np.zeros_like(list(predictions_dict.values())[0])
    for name, preds in predictions_dict.items():
        ensemble += weights.get(name, 0) * preds
    
    return ensemble


def time_based_split(
    df: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    date_column: str = 'date'
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data by time (chronological order)
    
    Args:
        df: DataFrame with date column
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        date_column: Name of date column
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    # Sort by date
    df = df.sort_values(date_column).reset_index(drop=True)
    
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]
    
    return train_df, val_df, test_df


def save_model_with_metadata(
    model: Any,
    market: str,
    metrics: Dict[str, float],
    feature_columns: List[str],
    model_type: str,
    calibration_model: Optional[Any] = None,
    calibration_method: Optional[str] = None,
    version: Optional[str] = None,
    train_start_date: Optional[str] = None,
    train_end_date: Optional[str] = None,
    additional_info: Optional[Dict] = None
) -> str:
    """
    Save model with comprehensive metadata
    
    Args:
        model: Trained model object
        market: Market name (goals, btts, cards, corners)
        metrics: Dictionary of evaluation metrics
        feature_columns: List of feature column names
        model_type: Type of model (e.g., 'xgboost', 'logistic')
        calibration_model: Calibration model (optional)
        calibration_method: Calibration method used (optional)
        version: Model version string (optional, will auto-generate if not provided)
        train_start_date: Training data start date
        train_end_date: Training data end date
        additional_info: Additional metadata to store
        
    Returns:
        Path to saved model
    """
    # Generate version if not provided
    if version is None:
        version = INITIAL_VERSION
    
    # Create model directory
    model_dir = MODELS_DIR / market
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = model_dir / f"{model_type}_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save calibration model if provided
    if calibration_model is not None:
        calib_path = model_dir / f"{model_type}_calibration.pkl"
        with open(calib_path, 'wb') as f:
            pickle.dump(calibration_model, f)
    
    # Create metadata
    metadata = {
        'market': market,
        'model_type': model_type,
        'version': version,
        'trained_at': datetime.now().isoformat(),
        'train_start_date': train_start_date,
        'train_end_date': train_end_date,
        'metrics': metrics,
        'feature_columns': feature_columns,
        'calibration_method': calibration_method,
        'has_calibration': calibration_model is not None
    }
    
    if additional_info:
        metadata.update(additional_info)
    
    # Save metadata
    metadata_path = model_dir / f"{model_type}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"💾 Saved {model_type} model for {market} to {model_path}")
    print(f"💾 Saved metadata to {metadata_path}")
    
    return str(model_path)


def load_model_with_metadata(
    market: str,
    model_type: str
) -> Tuple[Any, Dict, Optional[Any]]:
    """
    Load model with its metadata and calibration model
    
    Args:
        market: Market name (goals, btts, cards, corners)
        model_type: Type of model (e.g., 'xgboost', 'logistic')
        
    Returns:
        Tuple of (model, metadata_dict, calibration_model)
    """
    model_dir = MODELS_DIR / market
    
    # Load model
    model_path = model_dir / f"{model_type}_model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Load metadata
    metadata_path = model_dir / f"{model_type}_metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Load calibration model if exists
    calib_path = model_dir / f"{model_type}_calibration.pkl"
    calibration_model = None
    if calib_path.exists():
        with open(calib_path, 'rb') as f:
            calibration_model = pickle.load(f)
    
    return model, metadata, calibration_model


def increment_version(current_version: str, increment_type: str = 'minor') -> str:
    """
    Increment model version number
    
    Args:
        current_version: Current version string (e.g., 'v1.2.3')
        increment_type: 'major', 'minor', or 'patch'
        
    Returns:
        New version string
    """
    # Parse version
    version_str = current_version.replace('v', '')
    parts = version_str.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    # Increment
    if increment_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    elif increment_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Unknown increment type: {increment_type}")
    
    return f"v{major}.{minor}.{patch}"


def get_feature_importance(
    model: Any,
    feature_names: List[str],
    top_n: int = 20
) -> pd.DataFrame:
    """
    Extract feature importance from model
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        DataFrame with feature names and importance scores
    """
    if not hasattr(model, 'feature_importances_'):
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(top_n)
    
    return importance_df


def print_training_summary(
    market: str,
    model_type: str,
    metrics: Dict[str, float],
    train_samples: int,
    val_samples: int,
    test_samples: int = 0
):
    """
    Print formatted training summary
    
    Args:
        market: Market name
        model_type: Model type
        metrics: Dictionary of metrics
        train_samples: Number of training samples
        val_samples: Number of validation samples
        test_samples: Number of test samples (optional)
    """
    print("\n" + "=" * 60)
    print(f"TRAINING SUMMARY: {market.upper()} - {model_type.upper()}")
    print("=" * 60)
    print(f"Training samples:   {train_samples:,}")
    print(f"Validation samples: {val_samples:,}")
    if test_samples > 0:
        print(f"Test samples:       {test_samples:,}")
    print("\nMetrics:")
    for metric_name, value in metrics.items():
        print(f"  {metric_name:15s}: {value:.4f}")
    print("=" * 60)
