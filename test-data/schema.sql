-- Football Betting AI System - Database Schema
-- PostgreSQL 14+

-- Drop existing tables if they exist
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS match_odds CASCADE;
DROP TABLE IF EXISTS match_results CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS team_statistics CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- Teams table
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    league VARCHAR(50),
    tier VARCHAR(20), -- 'top', 'mid', 'lower'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team Statistics table (aggregated stats per team)
CREATE TABLE team_statistics (
    stat_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    season VARCHAR(10), -- '2022-23', '2023-24', etc.
    
    -- Overall stats
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    
    -- Home stats
    home_matches INTEGER DEFAULT 0,
    home_wins INTEGER DEFAULT 0,
    home_draws INTEGER DEFAULT 0,
    home_losses INTEGER DEFAULT 0,
    home_goals_scored INTEGER DEFAULT 0,
    home_goals_conceded INTEGER DEFAULT 0,
    
    -- Away stats
    away_matches INTEGER DEFAULT 0,
    away_wins INTEGER DEFAULT 0,
    away_draws INTEGER DEFAULT 0,
    away_losses INTEGER DEFAULT 0,
    away_goals_scored INTEGER DEFAULT 0,
    away_goals_conceded INTEGER DEFAULT 0,
    
    -- Averages (calculated fields)
    goals_avg DECIMAL(3,2),
    goals_conceded_avg DECIMAL(3,2),
    home_goals_avg DECIMAL(3,2),
    away_goals_avg DECIMAL(3,2),
    corners_avg DECIMAL(4,2),
    cards_avg DECIMAL(3,2),
    
    -- Rates
    btts_rate DECIMAL(3,2), -- Both teams to score rate
    clean_sheet_rate DECIMAL(3,2),
    
    -- Form (last 5 matches)
    current_form VARCHAR(5), -- e.g., 'WWDLW'
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team_id, season)
);

-- Matches table
CREATE TABLE matches (
    match_id VARCHAR(50) PRIMARY KEY,
    home_team_id INTEGER REFERENCES teams(team_id),
    away_team_id INTEGER REFERENCES teams(team_id),
    match_datetime TIMESTAMP NOT NULL,
    league VARCHAR(50),
    season VARCHAR(10),
    
    -- Match status
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
    
    -- Team stats at time of match (snapshot)
    home_goals_avg DECIMAL(3,2),
    away_goals_avg DECIMAL(3,2),
    home_goals_conceded_avg DECIMAL(3,2),
    away_goals_conceded_avg DECIMAL(3,2),
    home_corners_avg DECIMAL(4,2),
    away_corners_avg DECIMAL(4,2),
    home_cards_avg DECIMAL(3,2),
    away_cards_avg DECIMAL(3,2),
    home_btts_rate DECIMAL(3,2),
    away_btts_rate DECIMAL(3,2),
    home_form VARCHAR(5),
    away_form VARCHAR(5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match Results table (only for completed matches)
CREATE TABLE match_results (
    result_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) REFERENCES matches(match_id) ON DELETE CASCADE,
    
    -- Final score
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    
    -- Match outcome
    result VARCHAR(10), -- 'home_win', 'draw', 'away_win'
    
    -- Additional stats
    total_goals INTEGER,
    home_corners INTEGER,
    away_corners INTEGER,
    total_corners INTEGER,
    home_cards INTEGER,
    away_cards INTEGER,
    total_cards INTEGER,
    
    -- Market outcomes (boolean results)
    btts BOOLEAN, -- Both teams scored
    over_0_5 BOOLEAN,
    over_1_5 BOOLEAN,
    over_2_5 BOOLEAN,
    over_3_5 BOOLEAN,
    over_4_5 BOOLEAN,
    corners_over_8_5 BOOLEAN,
    corners_over_9_5 BOOLEAN,
    corners_over_10_5 BOOLEAN,
    cards_over_3_5 BOOLEAN,
    cards_over_4_5 BOOLEAN,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match Odds table (current and historical odds)
CREATE TABLE match_odds (
    odds_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) REFERENCES matches(match_id) ON DELETE CASCADE,
    
    -- Timestamp for odds snapshot
    odds_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Match Result (1X2)
    home_win_odds DECIMAL(5,2),
    draw_odds DECIMAL(5,2),
    away_win_odds DECIMAL(5,2),
    
    -- Total Goals Over/Under
    over_0_5_odds DECIMAL(5,2),
    under_0_5_odds DECIMAL(5,2),
    over_1_5_odds DECIMAL(5,2),
    under_1_5_odds DECIMAL(5,2),
    over_2_5_odds DECIMAL(5,2),
    under_2_5_odds DECIMAL(5,2),
    over_3_5_odds DECIMAL(5,2),
    under_3_5_odds DECIMAL(5,2),
    over_4_5_odds DECIMAL(5,2),
    under_4_5_odds DECIMAL(5,2),
    
    -- Both Teams To Score
    btts_yes_odds DECIMAL(5,2),
    btts_no_odds DECIMAL(5,2),
    
    -- Double Chance
    home_or_draw_odds DECIMAL(5,2),
    away_or_draw_odds DECIMAL(5,2),
    home_or_away_odds DECIMAL(5,2),
    
    -- Corners
    corners_over_8_5_odds DECIMAL(5,2),
    corners_under_8_5_odds DECIMAL(5,2),
    corners_over_9_5_odds DECIMAL(5,2),
    corners_under_9_5_odds DECIMAL(5,2),
    corners_over_10_5_odds DECIMAL(5,2),
    corners_under_10_5_odds DECIMAL(5,2),
    
    -- Cards
    cards_over_3_5_odds DECIMAL(5,2),
    cards_under_3_5_odds DECIMAL(5,2),
    cards_over_4_5_odds DECIMAL(5,2),
    cards_under_4_5_odds DECIMAL(5,2),
    
    -- Metadata
    bookmaker VARCHAR(50) DEFAULT 'test_bookmaker',
    is_latest BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table (AI model outputs)
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) REFERENCES matches(match_id) ON DELETE CASCADE,
    
    -- Prediction metadata
    model_version VARCHAR(20),
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Golden Bets (if applicable)
    is_golden_bet BOOLEAN DEFAULT false,
    golden_bet_market VARCHAR(50),
    golden_bet_selection VARCHAR(50),
    golden_bet_probability DECIMAL(4,3),
    golden_bet_confidence VARCHAR(20),
    
    -- Value Bets (if applicable)
    is_value_bet BOOLEAN DEFAULT false,
    value_bet_market VARCHAR(50),
    value_bet_selection VARCHAR(50),
    value_bet_ai_probability DECIMAL(4,3),
    value_bet_implied_probability DECIMAL(4,3),
    value_bet_value DECIMAL(4,3),
    
    -- Smart Bet (best per fixture)
    smart_bet_market VARCHAR(50),
    smart_bet_selection VARCHAR(50),
    smart_bet_probability DECIMAL(4,3),
    
    -- All market probabilities (JSON for flexibility)
    all_probabilities JSONB,
    
    -- Explanations
    explanation TEXT,
    key_factors JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_matches_datetime ON matches(match_datetime);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_home_team ON matches(home_team_id);
CREATE INDEX idx_matches_away_team ON matches(away_team_id);
CREATE INDEX idx_match_odds_match_id ON match_odds(match_id);
CREATE INDEX idx_match_odds_latest ON match_odds(match_id, is_latest);
CREATE INDEX idx_match_results_match_id ON match_results(match_id);
CREATE INDEX idx_predictions_match_id ON predictions(match_id);
CREATE INDEX idx_team_stats_team_season ON team_statistics(team_id, season);

-- Views for common queries

-- View: Upcoming matches with latest odds
CREATE VIEW upcoming_matches_with_odds AS
SELECT 
    m.*,
    ht.team_name as home_team_name,
    at.team_name as away_team_name,
    o.home_win_odds,
    o.draw_odds,
    o.away_win_odds,
    o.over_2_5_odds,
    o.under_2_5_odds,
    o.btts_yes_odds,
    o.btts_no_odds
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
LEFT JOIN match_odds o ON m.match_id = o.match_id AND o.is_latest = true
WHERE m.status = 'scheduled'
ORDER BY m.match_datetime;

-- View: Historical matches with results
CREATE VIEW historical_matches_with_results AS
SELECT 
    m.*,
    ht.team_name as home_team_name,
    at.team_name as away_team_name,
    r.home_goals,
    r.away_goals,
    r.result,
    r.total_goals,
    r.btts,
    o.home_win_odds,
    o.draw_odds,
    o.away_win_odds
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
JOIN match_results r ON m.match_id = r.match_id
LEFT JOIN match_odds o ON m.match_id = o.match_id AND o.is_latest = true
WHERE m.status = 'completed'
ORDER BY m.match_datetime DESC;

-- Comments
COMMENT ON TABLE teams IS 'Football teams in the system';
COMMENT ON TABLE team_statistics IS 'Aggregated team performance statistics per season';
COMMENT ON TABLE matches IS 'All matches (past and upcoming) with team stats snapshot';
COMMENT ON TABLE match_results IS 'Results for completed matches';
COMMENT ON TABLE match_odds IS 'Bookmaker odds (current and historical)';
COMMENT ON TABLE predictions IS 'AI model predictions for matches';
