"""
Model Training for Smart Bets AI
Trains separate models for each of the 4 target markets
"""

import os
import json
import pickle
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score, classification_report
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

from features import FeatureEngineer


class ModelTrainer:
    """
    Trains XGBoost models for the 4 target markets
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.metrics = {}
        
        # Model hyperparameters
        self.model_params = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss'
        }
    
    def load_training_data(self, data_path: str) -> pd.DataFrame:
        """
        Load historical match data for training
        
        Args:
            data_path: Path to JSON file with historical matches
            
        Returns:
            DataFrame with match data
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        matches = []
        for match in data.get('matches', []):
            # Extract match info
            match_data = {
                'match_id': match['match_id'],
                'match_datetime': match['match_datetime'],
                'season': match['season'],
                'league': match['league'],
                'status': match['status'],
                'home_team_id': match['home_team_id'],
                'home_team': match['home_team'],
                'away_team_id': match['away_team_id'],
                'away_team': match['away_team']
            }
            
            # Extract team stats
            stats = match.get('team_stats_at_match_time', {})
            match_data.update({
                'home_goals_avg': stats.get('home_goals_avg', 0),
                'away_goals_avg': stats.get('away_goals_avg', 0),
                'home_goals_conceded_avg': stats.get('home_goals_conceded_avg', 0),
                'away_goals_conceded_avg': stats.get('away_goals_conceded_avg', 0),
                'home_corners_avg': stats.get('home_corners_avg', 0),
                'away_corners_avg': stats.get('away_corners_avg', 0),
                'home_cards_avg': stats.get('home_cards_avg', 0),
                'away_cards_avg': stats.get('away_cards_avg', 0),
                'home_btts_rate': stats.get('home_btts_rate', 0),
                'away_btts_rate': stats.get('away_btts_rate', 0),
                'home_form': stats.get('home_form', ''),
                'away_form': stats.get('away_form', '')
            })
            
            # Extract results (targets)
            result = match.get('result', {})
            match_data.update({
                'home_goals': result.get('home_goals'),
                'away_goals': result.get('away_goals'),
                'result': result.get('result'),
                'total_goals': result.get('total_goals'),
                'home_corners': result.get('home_corners'),
                'away_corners': result.get('away_corners'),
                'total_corners': result.get('total_corners'),
                'home_cards': result.get('home_cards'),
                'away_cards': result.get('away_cards'),
                'total_cards': result.get('total_cards'),
                'btts': result.get('btts'),
                'over_2_5': result.get('over_2_5'),
                'corners_over_9_5': result.get('corners_over_9_5'),
                'cards_over_3_5': result.get('cards_over_3_5')
            })
            
            # Create btts_yes target
            match_data['btts_yes'] = match_data['btts']
            
            matches.append(match_data)
        
        df = pd.DataFrame(matches)
        print(f"✅ Loaded {len(df)} matches from {data_path}")
        return df
    
    def train_model(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        market: str
    ) -> XGBClassifier:
        """
        Train XGBoost model for a specific market
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            market: Market name (goals, cards, corners, btts)
            
        Returns:
            Trained XGBoost model
        """
        print(f"\n🔄 Training {market.upper()} model...")
        
        # Initialize model
        model = XGBClassifier(**self.model_params)
        
        # Train with early stopping
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        accuracy = accuracy_score(y_val, y_pred)
        logloss = log_loss(y_val, y_pred_proba)
        
        try:
            auc = roc_auc_score(y_val, y_pred_proba)
        except:
            auc = 0.0
        
        # Store metrics
        self.metrics[market] = {
            'accuracy': float(accuracy),
            'log_loss': float(logloss),
            'auc_roc': float(auc),
            'training_samples': len(X_train),
            'validation_samples': len(X_val)
        }
        
        print(f"✅ {market.upper()} Model Performance:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   Log Loss: {logloss:.4f}")
        print(f"   AUC-ROC: {auc:.4f}")
        
        return model
    
    def train_all_markets(self, data_path: str, test_size: float = 0.2):
        """
        Train models for all 4 target markets
        
        Args:
            data_path: Path to historical match data
            test_size: Proportion of data for validation
        """
        print("=" * 60)
        print("SMART BETS AI - MODEL TRAINING")
        print("=" * 60)
        
        # Load data
        df = self.load_training_data(data_path)
        
        # Train model for each market
        markets = ['goals', 'cards', 'corners', 'btts']
        
        for market in markets:
            try:
                # Prepare data
                X, y = self.feature_engineer.prepare_training_data(df, market)
                
                # Split data
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )
                
                # Train model
                model = self.train_model(X_train, y_train, X_val, y_val, market)
                
                # Store model
                self.models[market] = model
                
            except Exception as e:
                print(f"❌ Error training {market} model: {e}")
                continue
        
        # Save models and metadata
        self.save_models()
        
        print("\n" + "=" * 60)
        print("✅ TRAINING COMPLETE")
        print("=" * 60)
    
    def save_models(self):
        """Save trained models and metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save each model
        for market, model in self.models.items():
            model_path = self.models_dir / f"{market}_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"💾 Saved {market} model to {model_path}")
        
        # Save feature engineer
        fe_path = self.models_dir / "feature_engineer.pkl"
        with open(fe_path, 'wb') as f:
            pickle.dump(self.feature_engineer, f)
        print(f"💾 Saved feature engineer to {fe_path}")
        
        # Save metadata
        metadata = {
            'version': '1.0.0',
            'trained_at': timestamp,
            'markets': list(self.models.keys()),
            'metrics': self.metrics,
            'feature_columns': self.feature_engineer.get_feature_columns(),
            'model_params': self.model_params
        }
        
        metadata_path = self.models_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved metadata to {metadata_path}")
    
    def load_models(self):
        """Load trained models from disk"""
        markets = ['goals', 'cards', 'corners', 'btts']
        
        for market in markets:
            model_path = self.models_dir / f"{market}_model.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    self.models[market] = pickle.load(f)
                print(f"✅ Loaded {market} model")
        
        # Load feature engineer
        fe_path = self.models_dir / "feature_engineer.pkl"
        if fe_path.exists():
            with open(fe_path, 'rb') as f:
                self.feature_engineer = pickle.load(f)
            print(f"✅ Loaded feature engineer")
        
        # Load metadata
        metadata_path = self.models_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.metrics = json.load(f).get('metrics', {})
            print(f"✅ Loaded metadata")


def main():
    """Main training function"""
    # Initialize trainer
    trainer = ModelTrainer(models_dir="smart-bets-ai/models")
    
    # Train on historical data
    data_path = "test-data/historical_matches_sample.json"
    
    if not os.path.exists(data_path):
        print(f"❌ Training data not found at {data_path}")
        print("Please ensure historical match data is available")
        return
    
    # Train all models
    trainer.train_all_markets(data_path)


if __name__ == "__main__":
    main()
