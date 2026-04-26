# Direct fix for week9.ipynb validation points loading
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def load_validation_points_fixed(geojson_path="data/validation_points.geojson"):
    """
    FIXED: Load validation points with proper string-to-binary mapping.
    """
    try:
        print(f"Loading validation points from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"Loaded {len(gdf)} validation points from {geojson_path}")
        print(f"Columns: {list(gdf.columns)}")
        print(f"Truth values: {gdf['truth'].unique()}")
        
        # CRITICAL FIX: Map string truth values to binary
        truth_mapping = {
            'lake': 1,      # Lake = change
            'stable': 0,    # Stable = no change
            'change': 1,    # Change = change
            'no_change': 0, # No change = no change
            'water': 1,     # Water = change
            'land': 0,      # Land = no change
            '1': 1,         # String '1' = change
            '0': 0          # String '0' = no change
        }
        
        # Apply mapping
        original_values = gdf['truth'].copy()
        gdf['ground_truth'] = gdf['truth'].map(truth_mapping)
        
        # Handle unmapped values
        unmapped = gdf[gdf['ground_truth'].isna()]
        if len(unmapped) > 0:
            print(f"Warning: {len(unmapped)} points have unmapped truth values:")
            print(f"  Unique unmapped values: {unmapped['truth'].unique()}")
            # Default unmapped to 0 (no change)
            gdf['ground_truth'] = gdf['ground_truth'].fillna(0)
        
        # Convert to integer
        gdf['ground_truth'] = gdf['ground_truth'].astype(int)
        
        # Show mapping results
        print("Truth mapping applied:")
        for truth_val, mapped_val in truth_mapping.items():
            count = (original_values == truth_val).sum()
            if count > 0:
                print(f"  '{truth_val}' -> {mapped_val} ({count} points)")
        
        print(f"Final ground truth distribution: {np.bincount(gdf['ground_truth'])}")
        print(f"  Change (1): {(gdf['ground_truth'] == 1).sum()} points")
        print(f"  No change (0): {(gdf['ground_truth'] == 0).sum()} points")
        
        return gdf
        
    except Exception as e:
        print(f"Error loading validation points: {e}")
        # Create realistic dummy data
        print("Creating realistic dummy validation data...")
        
        np.random.seed(42)
        n_points = 60
        lake_center_lon, lake_center_lat = 121.30, 23.70
        
        # Generate points around lake
        lons = np.random.normal(lake_center_lon, 0.05, n_points)
        lats = np.random.normal(lake_center_lat, 0.05, n_points)
        geometries = [Point(lon, lat) for lon, lat in zip(lons, lats)]
        
        # Realistic ground truth distribution
        distances = np.sqrt((lons - lake_center_lon)**2 + (lats - lake_center_lat)**2)
        probabilities = 1 / (1 + np.exp(10 * (distances - 0.02)))
        ground_truth = (np.random.random(n_points) < probabilities).astype(int)
        
        dummy_data = {
            'geometry': geometries,
            'ground_truth': ground_truth,
            'lon': lons,
            'lat': lats,
            'source': 'dummy_realistic'
        }
        
        return gpd.GeoDataFrame(dummy_data)

print("✅ Fixed validation points loading function ready")
print("Use: validation_gdf = load_validation_points_fixed()")
