# Environment integration for week9.ipynb
import pandas as pd
import numpy as np
import time
from pystac_client import Client

def load_env_config():
    """Load environment configuration from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                env_vars[key] = value
        
        print("✅ Environment variables loaded from .env file")
        return env_vars
        
    except FileNotFoundError:
        print("⚠️  .env file not found, using default values")
        return {}
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return {}

def extract_env_date_config():
    """Extract date configuration from environment variables"""
    ENV_VARS = load_env_config()
    
    # Date ranges from environment
    date_ranges = {
        'Pre': {
            'start': ENV_VARS.get('PRE_EVENT_START', '2025-06-01'),
            'end': ENV_VARS.get('PRE_EVENT_END', '2025-07-15')
        },
        'Mid': {
            'start': ENV_VARS.get('MID_EVENT_START', '2025-08-01'),
            'end': ENV_VARS.get('MID_EVENT_END', '2025-09-20')
        },
        'Post': {
            'start': ENV_VARS.get('POST_EVENT_START', '2025-09-25'),
            'end': ENV_VARS.get('POST_EVENT_END', '2025-11-15')
        }
    }
    
    # Calculate target dates and search ranges
    target_dates = {}
    search_ranges = {}
    
    for period, dates in date_ranges.items():
        start = pd.to_datetime(dates['start'])
        end = pd.to_datetime(dates['end'])
        target = start + (end - start) / 2
        target_dates[period] = target.strftime('%Y-%m-%d')
        
        duration_days = (end - start).days
        search_ranges[period] = duration_days // 2
    
    return date_ranges, target_dates, search_ranges

# Cloud weights with Mid 10x priority
CLOUD_WEIGHTS = {
    'Pre': 3,    # 3x weight for Pre scene
    'Mid': 10,   # 10x weight for Mid scene (CRITICAL)
    'Post': 3     # 3x weight for Post scene
}

def robust_search_env_mid_priority(client, bbox, period='Mid', max_retries=3):
    """
    Enhanced search with environment dates and Mid 10x cloud priority.
    """
    date_ranges, target_dates, search_ranges = extract_env_date_config()
    
    if period not in target_dates:
        print(f"❌ Unknown period: {period}")
        return None
    
    target_date = target_dates[period]
    date_range = search_ranges[period]
    cloud_weight = CLOUD_WEIGHTS[period]
    
    print(f"\n🔍 Searching {period} scene with ENV config:")
    print(f"  📅 Date range: {date_ranges[period]['start']} to {date_ranges[period]['end']}")
    print(f"  🎯 Target date: {target_date}")
    print(f"  🔍 Search range: ±{date_range} days")
    print(f"  ⚖️  Cloud weight: {cloud_weight}x")
    
    for attempt in range(max_retries):
        try:
            target_dt = pd.to_datetime(target_date).tz_localize('UTC')
            start_date_search = (target_dt - pd.Timedelta(days=date_range)).strftime('%Y-%m-%d')
            end_date_search = (target_dt + pd.Timedelta(days=date_range)).strftime('%Y-%m-%d')

            print(f"  Attempt {attempt + 1}/{max_retries}: Searching from {start_date_search} to {end_date_search}")
            
            search_results = client.search(
                collections=['sentinel-2-l2a'],
                bbox=bbox,
                datetime=f'{start_date_search}T00:00:00Z/{end_date_search}T23:59:59Z',
                max_items=35
            )
            item_collection = search_results.item_collection()
            
            if not item_collection.items:
                print(f"  No items found for {period} in range.")
                return None
            
            scene_candidates = []
            print(f"  Analyzing {len(item_collection.items)} scenes for cloud coverage...")
            
            for item in item_collection.items:
                item_date = pd.to_datetime(item.properties['datetime']).tz_convert('UTC')
                date_diff = abs((item_date - target_dt).days)
                cloud_coverage = item.properties.get('eo:cloud_cover', 100)
                
                # CRITICAL: Mid period gets 10x cloud weight
                score = (cloud_coverage * cloud_weight) + (date_diff * 1)
                
                scene_candidates.append({
                    'item': item,
                    'date': item_date,
                    'date_diff': date_diff,
                    'cloud_coverage': cloud_coverage,
                    'score': score,
                    'cloud_weight': cloud_weight
                })
            
            scene_candidates.sort(key=lambda x: x['score'])
            
            print(f"  Top 5 scene candidates ({period} - Cloud weight {cloud_weight}x):")
            for i, candidate in enumerate(scene_candidates[:5]):
                cloud_weight_score = candidate['cloud_coverage'] * candidate['cloud_weight']
                date_weight = candidate['date_diff'] * 1
                print(f"    {i+1}. {candidate['date'].strftime('%Y-%m-%d')} - "
                      f"Cloud: {candidate['cloud_coverage']:.1f}% (weight: {cloud_weight_score:.1f}) - "
                      f"Date diff: {candidate['date_diff']} days (weight: {date_weight:.1f}) - "
                      f"Total Score: {candidate['score']:.1f}")
            
            best_candidate = scene_candidates[0]
            best_item = best_candidate['item']
            
            print(f"  ✓ SELECTED: {best_candidate['date'].strftime('%Y-%m-%d')} "
                  f"(Cloud: {best_candidate['cloud_coverage']:.1f}%, "
                  f"Date diff: {best_candidate['date_diff']} days, "
                  f"Score: {best_candidate['score']:.1f})")
            
            # Period-specific warnings
            if period == 'Mid':
                if best_candidate['cloud_coverage'] > 15:
                    print(f"  🚨 CRITICAL: Mid scene cloud coverage {best_candidate['cloud_coverage']:.1f}% > 15%!")
                elif best_candidate['cloud_coverage'] > 10:
                    print(f"  ⚠️  WARNING: Mid scene cloud coverage {best_candidate['cloud_coverage']:.1f}% > 10%")
                elif best_candidate['cloud_coverage'] > 5:
                    print(f"  🟡 CAUTION: Mid scene cloud coverage {best_candidate['cloud_coverage']:.1f}% > 5%")
                else:
                    print(f"  ✅ PERFECT: Mid scene cloud coverage {best_candidate['cloud_coverage']:.1f}% < 5%")
            else:
                if best_candidate['cloud_coverage'] > 30:
                    print(f"  ⚠️  WARNING: {period} scene has high cloud coverage ({best_candidate['cloud_coverage']:.1f}%)")
                elif best_candidate['cloud_coverage'] > 20:
                    print(f"  🟡 CAUTION: {period} scene has moderate cloud coverage ({best_candidate['cloud_coverage']:.1f}%)")
                else:
                    print(f"  ✅ GOOD: {period} scene has low cloud coverage ({best_candidate['cloud_coverage']:.1f}%)")
            
            return best_item
            
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {str(e)[:100]}...")
            if attempt < max_retries - 1:
                print(f"  Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"  All {max_retries} attempts failed for {period}")
                return None

def load_real_sentinel2_data_with_env():
    """
    Load real Sentinel-2 data using environment configuration.
    """
    print("=" * 80)
    print("LOADING REAL SENTINEL-2 DATA FOR MATAI'AN BARRIER LAKE")
    print("📅 USING ENVIRONMENT-BASED DATE CONFIGURATION")
    print("🎯 MID PERIOD: 10x CLOUD WEIGHT")
    print("=" * 80)
    
    # Show environment configuration
    date_ranges, target_dates, search_ranges = extract_env_date_config()
    print("\n📅 Environment Configuration:")
    for period in ['Pre', 'Mid', 'Post']:
        print(f"  {period}: {date_ranges[period]['start']} to {date_ranges[period]['end']}")
        print(f"    Target: {target_dates[period]}, Search: ±{search_ranges[period]} days")
    
    print(f"\n🎯 Cloud weights: Pre={CLOUD_WEIGHTS['Pre']}x, Mid={CLOUD_WEIGHTS['Mid']}x, Post={CLOUD_WEIGHTS['Post']}x")
    
    # Create STAC client
    STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
    client = Client.open(STAC_API_URL)
    
    # Search for scenes
    scenes = {}
    for period in ['Pre', 'Mid', 'Post']:
        item = robust_search_env_mid_priority(client, MATAIAN_BBOX, period)
        if item:
            scenes[period] = item
        else:
            print(f"❌ Warning: Could not find a suitable scene for {period}")
    
    print(f"\n✅ Scenes found: {list(scenes.keys())}")
    
    return scenes

print("✅ Environment integration functions loaded")
print("📅 Will use .env file date ranges with Mid 10x cloud priority")
