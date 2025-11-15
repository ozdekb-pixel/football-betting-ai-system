"""
Value Bets Calculator
Refactored to use integrated predictor with systematic value calculation
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from predictor.integrated_predictor import IntegratedPredictor


class ValueBetsCalculator:
    """
    Systematic value betting calculator using trained models
    """
    
    def __init__(
        self,
        min_value_pct: float = 5.0,
        min_ev: float = 0.05,
        min_prob: float = 0.40
    ):
        """
        Initialize Value Bets calculator
        
        Args:
            min_value_pct: Minimum value percentage
            min_ev: Minimum expected value
            min_prob: Minimum AI probability
        """
        self.min_value_pct = min_value_pct
        self.min_ev = min_ev
        self.min_prob = min_prob
        self.predictor = IntegratedPredictor()
    
    def find_value_bets(self, predictions_with_odds: List[Dict]) -> List[Dict]:
        """
        Find value bets from predictions with odds
        
        Args:
            predictions_with_odds: List of dicts with match_data, market, odds
            
        Returns:
            List of value bets with calculations
        """
        value_bets = []
        
        for pred in predictions_with_odds:
            match_data = pred.get('match_data', {})
            market = pred.get('market', 'goals')
            odds = pred.get('odds', 2.0)
            
            # Get AI probability
            ai_prob = self.predictor.predict_for_match(market, match_data)
            
            # Skip if below minimum probability
            if ai_prob < self.min_prob:
                continue
            
            # Calculate value
            implied_prob = 1 / odds
            fair_odds = 1 / ai_prob
            value_pct = ((ai_prob / implied_prob) - 1) * 100
            ev = (ai_prob * odds) - 1
            
            # Check if meets value criteria
            if value_pct >= self.min_value_pct and ev >= self.min_ev:
                value_bets.append({
                    'match_id': pred.get('match_id'),
                    'league': pred.get('league', ''),
                    'market': market,
                    'ai_probability': ai_prob,
                    'implied_probability': implied_prob,
                    'odds': odds,
                    'fair_odds': fair_odds,
                    'value_pct': value_pct,
                    'expected_value': ev,
                    'match_data': match_data
                })
        
        # Sort by value percentage
        value_bets.sort(key=lambda x: x['value_pct'], reverse=True)
        return value_bets
    
    def format_value_bet(self, bet: Dict) -> Dict:
        """
        Format value bet for API response
        
        Args:
            bet: Value bet dictionary
            
        Returns:
            Formatted response
        """
        market_names = {
            'goals': 'Over 2.5 Goals',
            'btts': 'Both Teams To Score - Yes',
            'cards': 'Over 3.5 Cards',
            'corners': 'Over 9.5 Corners'
        }
        
        return {
            'match_id': bet['match_id'],
            'league': bet['league'],
            'market_name': market_names.get(bet['market'], bet['market']),
            'selection': market_names.get(bet['market'], bet['market']),
            'ai_probability': bet['ai_probability'],
            'ai_percentage': f"{bet['ai_probability'] * 100:.1f}%",
            'odds': bet['odds'],
            'fair_odds': round(bet['fair_odds'], 2),
            'value_percentage': f"{bet['value_pct']:.1f}%",
            'expected_value': f"{bet['expected_value']:.2%}",
            'implied_probability': f"{bet['implied_probability']:.1%}"
        }
