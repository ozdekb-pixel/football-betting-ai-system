#!/usr/bin/env python3
"""
Load test data into database
Reads JSON files and ingests them via the data ingestion service
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_ingestion.database import get_db, init_db
from data_ingestion.ingestion import DataIngestionService
from data_ingestion.schemas import BatchIngestRequest


def load_json_file(filepath: str) -> dict:
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_historical_matches():
    """Load historical matches from test data"""
    print("\n📊 Loading historical matches...")
    
    # Try different file names
    test_files = [
        'test-data/historical_matches_300_generated.json',
        'test-data/historical_matches_300.json',
        'test-data/historical_matches_sample.json'
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"✅ Found: {filepath}")
            data = load_json_file(filepath)
            matches = data.get('matches', [])
            
            if matches:
                with get_db() as db:
                    service = DataIngestionService(db)
                    request = BatchIngestRequest(matches=matches)
                    response = service.ingest_batch(request)
                    
                    print(f"✅ Processed {response.matches_processed} matches")
                    print(f"   Created: {response.matches_created}")
                    print(f"   Updated: {response.matches_updated}")
                    
                    if response.errors:
                        print(f"⚠️  Errors: {len(response.errors)}")
                        for error in response.errors[:5]:  # Show first 5 errors
                            print(f"   - {error}")
                
                return True
    
    print("❌ No historical match files found")
    return False


def load_upcoming_fixtures():
    """Load upcoming fixtures from test data"""
    print("\n📅 Loading upcoming fixtures...")
    
    test_files = [
        'test-data/upcoming_fixtures_200_generated.json',
        'test-data/upcoming_fixtures_200.json'
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"✅ Found: {filepath}")
            data = load_json_file(filepath)
            fixtures = data.get('fixtures', [])
            
            if fixtures:
                with get_db() as db:
                    service = DataIngestionService(db)
                    request = BatchIngestRequest(matches=fixtures)
                    response = service.ingest_batch(request)
                    
                    print(f"✅ Processed {response.matches_processed} fixtures")
                    print(f"   Created: {response.matches_created}")
                    print(f"   Updated: {response.matches_updated}")
                    
                    if response.errors:
                        print(f"⚠️  Errors: {len(response.errors)}")
                        for error in response.errors[:5]:
                            print(f"   - {error}")
                
                return True
    
    print("❌ No upcoming fixture files found")
    return False


def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 Football Betting AI - Test Data Loader")
    print("=" * 60)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Load data
    historical_loaded = load_historical_matches()
    fixtures_loaded = load_upcoming_fixtures()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Historical matches: {'✅ Loaded' if historical_loaded else '❌ Not loaded'}")
    print(f"Upcoming fixtures: {'✅ Loaded' if fixtures_loaded else '❌ Not loaded'}")
    print("\n✅ Data loading complete!")
    print("\n💡 Next steps:")
    print("   1. Start the API: uvicorn user-api.main:app --reload")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Test endpoints: GET /api/v1/matches")


if __name__ == "__main__":
    main()
