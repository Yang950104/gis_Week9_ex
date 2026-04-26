# Real Task 4 Execution - Fixed version with proper threshold handling
import numpy as np
import matplotlib.pyplot as plt
import os

def execute_real_task4(task1_results, optimal_threshold, output_dir="output"):
    """
    Execute Task 4 with real Sentinel-2 data.
    
    Args:
        task1_results: Real results from Task 1
        optimal_threshold: Optimal threshold from Task 2
        output_dir: Output directory
        
    Returns:
        Dictionary with Task 4 results
    """
    print("=" * 60)
    print("TASK 4: CONFIDENCE MAP WITH REAL DATA")
    print("=" * 60)
    
    try:
        # Check if we have real data
        if 'real_data_info' not in task1_results:
            print("❌ Error: task1_results does not contain real data")
            print("Please execute Task 1 with real Sentinel-2 data first")
            return None
        
        print(f"✅ Using real data: {task1_results['real_data_info']['data_type']}")
        print(f"✅ Optimal threshold: {optimal_threshold:.4f}")
        
        # Get real data
        delta_ndvi = task1_results['masked_differences']['delta_NDVI_mid_pre']
        ndwi_pre = task1_results['indices_pre']['NDWI']
        ndwi_mid = Task1_results['indices_mid']['NDWI']
        ndwi_post = Task1_results['indices_post']['NDWI']
        
        print(f"ΔNDVI shape: {delta_ndvi.shape}")
        print(f"NDWI shapes - Pre: {ndwi_pre.shape}, Mid: {ndwi_mid.shape}, Post: {ndwi_post.shape}")
        
        # Create confidence map
        print("Creating confidence zones...")
        confidence_map = np.zeros_like(delta_ndvi, dtype=int)
        
        # Define zones based on ΔNDVI
        high_confidence_mask = (delta_ndvi < optimal_threshold * 1.2)  # Much lower than threshold
        confidence_map[high_confidence_mask] = 1
        
        medium_confidence_mask = (delta_ndvi >= optimal_threshold * 1.2) & (delta_ndvi < optimal_threshold * 0.8)
        confidence_map[medium_confidence_mask] = 2
        
        low_confidence_mask = (delta_ndvi >= optimal_threshold * 0.8) & (delta_ndvi < optimal_threshold * 0.5)
        confidence_map[low_confidence_mask] = 3
        
        no_confidence_mask = (delta_ndvi >= optimal_threshold * 0.5)
        confidence_map[no_confidence_mask] = 4
        
        # Calculate areas
        pixel_area_km2 = 0.01  # 10m x 10m = 100m² = 0.0001km²
        zone_stats = {}
        
        zone_names = {1: "High Confidence", 2: "Medium Confidence", 3: "Low Confidence", 4: "No Confidence"}
        for zone_id, zone_name in zone_names.items():
            pixels = np.sum(confidence_map == zone_id)
            area_km2 = pixels * pixel_area_km2
            percentage = (pixels / confidence_map.size) * 100
            zone_stats[zone_name] = {
                'pixels': int(pixels),
                'area_km2': float(area_km2),
                'percentage': float(percentage)
            }
        
        print("Confidence zone statistics:")
        for zone_name, stats in zone_stats.items():
            print(f"  {zone_name}: {stats['pixels']:,} pixels ({stats['area_km2']:.3f} km², {stats['percentage']:.1f}%)")
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Real Task 4: Confidence Map & Water Analysis\nMatai\'an Barrier Lake', 
                     fontsize=16, fontweight='bold')
        
        # Subplot 1: Confidence map
        colors = ['#d73027', '#fc8d59', '#fee08b', '#1a9850']  # Red, Orange, Yellow, Green
        cmap = plt.matplotlib.colors.ListedColormap(colors, N=4)
        im1 = axes[0, 0].imshow(confidence_map, cmap=cmap, vmin=1, vmax=4)
        axes[0, 0].set_title('Confidence Map\nBased on Real ΔNDVI', fontweight='bold')
        axes[0, 0].set_xlabel('X (pixels)')
        axes[0, 0].set_ylabel('Y (pixels)')
        plt.colorbar(im1, ax=axes[0, 0], ticks=[1, 2, 3, 4], 
                     label=['High', 'Medium', 'Low', 'No'])
        
        # Subplot 2: NDWI Mid (water detection)
        im2 = axes[0, 1].imshow(ndwi_mid, cmap='Blues_r', vmin=-0.5, vmax=0.5)
        axes[0, 1].set_title('Mid-Disaster NDWI\nReal Water Detection', fontweight='bold')
        axes[0, 1].set_xlabel('X (pixels)')
        axes[0, 1].set_ylabel('Y (pixels)')
        plt.colorbar(im2, ax=axes[0, 1], label='NDWI')
        
        # Subplot 3: NDWI Pre
        im3 = axes[1, 0].imshow(ndwi_pre, cmap='Blues_r', vmin=-0.5, vmax=0.5)
        axes[1, 0].set_title('Pre-Disaster NDWI\nBefore Event', fontweight='bold')
        axes[1, 0].set_xlabel('X (pixels)')
        axes[1, 0].set_ylabel('Y (pixels)')
        plt.colorbar(im3, ax=axes[1, 0], label='NDWI')
        
        # Subplot 4: NDWI Post
        im4 = axes[1, 1].imshow(ndwi_post, cmap='Blues_r', vmin=-0.5, vmax=0.5)
        axes[1, 1].set_title('Post-Disaster NDWI\nAfter Event', fontweight='bold')
        axes[1, 1].set_xlabel('X (pixels)')
        axes[1, 1].set_ylabel('Y (pixels)')
        plt.colorbar(im4, ax=axes[1, 1], label='NDWI')
        
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(output_dir, 'task4_real_confidence_map.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\nTask 4 results saved to: {output_path}")
        
        # Water statistics
        pre_water = np.sum(ndwi_pre > 0)
        mid_water = np.sum(ndwi_mid > 0)
        post_water = np.sum(ndwi_post > 0)
        
        print(f"\nWater detection statistics:")
        print(f"  Pre event water pixels: {pre_water:,}")
        print(f"  Mid event water pixels: {mid_water:,}")
        print(f"  Post event water pixels: {post_water:,}")
        print(f"  Water change (Pre→Mid): {mid_water - pre_water:+,}")
        print(f"  Water change (Mid→Post): {post_water - mid_water:+,}")
        
        return {
            'confidence_map': confidence_map,
            'zone_statistics': zone_stats,
            'water_statistics': {
                'pre_water_pixels': int(pre_water),
                'mid_water_pixels': int(mid_water),
                'post_water_pixels': int(post_water),
                'change_pre_mid': int(mid_water - pre_water),
                'change_mid_post': int(post_water - mid_water)
            },
            'optimal_threshold': optimal_threshold,
            'data_type': 'real_sentinel2'
        }
        
    except Exception as e:
        print(f"❌ Error executing Task 4: {e}")
        import traceback
        traceback.print_exc()
        return None

print("✅ Real Task 4 execution function loaded!")
print("Usage: results = execute_real_task4(task1_real_results, optimal_threshold)")
print("Note: Make sure optimal_threshold is defined from Task 2")
