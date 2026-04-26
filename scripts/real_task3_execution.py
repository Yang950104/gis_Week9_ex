# Real Task 3 Execution - Use actual Task 1 results
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.transform import from_bounds

# Load all necessary fixes
exec(open('fix_validation_week9.py').read())

def execute_real_task3_workflow(task1_real_results):
    """
    Execute Task 3 using REAL Task 1 results from actual Sentinel-2 data.
    
    Args:
        task1_real_results: Real results from Task 1 with actual Sentinel-2 data
        
    Returns:
        Dictionary with all assessment results using real data
    """
    print("=" * 80)
    print("REAL TASK 3 WORKFLOW: Using Actual Sentinel-2 Data")
    print("=" * 80)
    
    # Verify we have real data
    if task1_real_results is None:
        print("❌ Error: task1_real_results is None")
        print("Please execute Task 1 with real data first:")
        print("task1_real_results = execute_task1_with_real_data()")
        return None
    
    if 'real_data_info' not in task1_real_results:
        print("❌ Error: task1_real_results does not contain real data")
        print("This appears to be dummy data, not real Sentinel-2 data")
        return None
    
    print(f"✅ Using real Sentinel-2 data")
    print(f"   Data type: {task1_real_results['real_data_info']['data_type']}")
    print(f"   Cube shape: {task1_real_results['real_data_info']['cube_shape']}")
    
    # Step 1: Load fixed validation points
    print("\n📊 Step 1: Loading validation points...")
    validation_gdf = load_validation_points_fixed()
    print(f"✅ Loaded {len(validation_gdf)} validation points")
    
    # Step 2: Get real ΔNDVI difference map
    print("\n🔍 Step 2: Extracting real ΔNDVI data...")
    delta_ndvi = task1_real_results['masked_differences']['delta_NDVI_mid_pre']
    print(f"✅ ΔNDVI shape: {delta_ndvi.shape}")
    print(f"   ΔNDVI range: [{np.nanmin(delta_ndvi):.3f}, {np.nanmax(delta_ndvi):.3f}]")
    print(f"   Valid pixels: {(~np.isnan(delta_ndvi)).sum():,}")
    
    # Step 3: Create real transform
    print("\n📍 Step 3: Creating geospatial transform...")
    transform = from_bounds(*MATAIAN_BBOX, delta_ndvi.shape[1], delta_ndvi.shape[0])
    print(f"✅ Transform created for bounding box: {MATAIAN_BBOX}")
    
    # Step 4: Extract real pixel values at validation points
    print("\n📈 Step 4: Extracting pixel values at validation points...")
    pixel_values, ground_truth = extract_pixel_values_at_validation_points(
        delta_ndvi, validation_gdf, transform
    )
    print(f"✅ Extracted {len(pixel_values)} valid pixel values")
    print(f"   Ground truth distribution: {np.bincount(ground_truth)}")
    print(f"   Pixel value range: [{np.min(pixel_values):.3f}, {np.max(pixel_values):.3f}]")
    
    # Step 5: Real threshold optimization
    print("\n🎯 Step 5: Performing real threshold optimization...")
    thresholds = np.linspace(-0.1, -0.5, 20)
    results = []
    
    for threshold in thresholds:
        predictions = (pixel_values < threshold).astype(int)
        
        # Calculate confusion matrix
        tp = np.sum((predictions == 1) & (ground_truth == 1))
        fp = np.sum((predictions == 1) & (ground_truth == 0))
        tn = np.sum((predictions == 0) & (ground_truth == 0))
        fn = np.sum((predictions == 0) & (ground_truth == 1))
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        
        results.append({
            'threshold': threshold,
            'F1': f1,
            'Producer_Accuracy': recall,  # Producer's Accuracy = Recall
            'User_Accuracy': precision,   # User's Accuracy = Precision
            'Overall_Accuracy': accuracy,
            'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn
        })
    
    results_df = pd.DataFrame(results)
    optimal_threshold = results_df.loc[results_df['F1'].idxmax(), 'threshold']
    optimal_metrics = results_df.loc[results_df['F1'].idxmax()]
    
    print(f"✅ Optimal threshold: {optimal_threshold:.4f}")
    print(f"   F1-Score: {optimal_metrics['F1']:.3f}")
    print(f"   Producer's Accuracy: {optimal_metrics['Producer_Accuracy']:.3f}")
    print(f"   User's Accuracy: {optimal_metrics['User_Accuracy']:.3f}")
    
    # Step 6: Generate real change map
    print("\n🗺️  Step 6: Generating real change map...")
    change_map = (delta_ndvi < optimal_threshold).astype(int)
    change_pixels = change_map.sum()
    total_pixels = change_map.size
    change_percentage = (change_pixels / total_pixels) * 100
    
    print(f"✅ Change detection results:")
    print(f"   Change pixels: {change_pixels:,}/{total_pixels:,} ({change_percentage:.1f}%)")
    print(f"   No change pixels: {total_pixels - change_pixels:,} ({100 - change_percentage:.1f}%)")
    
    # Step 7: Create comprehensive visualization
    print("\n📊 Step 7: Creating visualization...")
    create_real_task3_visualization(delta_ndvi, change_map, validation_gdf, 
                                   transform, pixel_values, ground_truth, 
                                   optimal_threshold, results_df)
    
    # Step 8: Calculate final confusion matrix
    print("\n📈 Step 8: Final accuracy assessment...")
    final_predictions = (pixel_values < optimal_threshold).astype(int)
    
    tp = np.sum((final_predictions == 1) & (ground_truth == 1))
    fp = np.sum((final_predictions == 1) & (ground_truth == 0))
    tn = np.sum((final_predictions == 0) & (ground_truth == 0))
    fn = np.sum((final_predictions == 0) & (ground_truth == 1))
    
    confusion_matrix = np.array([[tn, fp], [fn, tp]])
    
    final_accuracy = (tp + tn) / (tp + tn + fp + fn)
    final_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    final_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    final_f1 = 2 * (final_precision * final_recall) / (final_precision + final_recall) if (final_precision + final_recall) > 0 else 0
    
    print(f"✅ Final Assessment Results:")
    print(f"   Overall Accuracy: {final_accuracy:.3f}")
    print(f"   Precision: {final_precision:.3f}")
    print(f"   Recall: {final_recall:.3f}")
    print(f"   F1-Score: {final_f1:.3f}")
    print(f"   Confusion Matrix:")
    print(f"     [[{tn}, {fp}],")
    print(f"      [{fn}, {tp}]]")
    
    return {
        'change_map': change_map,
        'confusion_matrix': confusion_matrix,
        'optimal_threshold': optimal_threshold,
        'accuracy': final_accuracy,
        'precision': final_precision,
        'recall': final_recall,
        'f1_score': final_f1,
        'change_percentage': change_percentage,
        'threshold_results': results_df,
        'validation_points': len(validation_gdf),
        'valid_pixels': len(pixel_values),
        'data_type': 'real_sentinel2'
    }

def create_real_task3_visualization(delta_ndvi, change_map, validation_gdf, 
                                   transform, pixel_values, ground_truth, 
                                   optimal_threshold, results_df):
    """
    Create comprehensive visualization for real Task 3 results.
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Task 3: Real Sentinel-2 Accuracy Assessment\nMatai\'an Barrier Lake', 
                 fontsize=16, fontweight='bold')
    
    # 1. Real ΔNDVI difference map
    im1 = axes[0, 0].imshow(delta_ndvi, cmap='RdYlGn', vmin=-0.5, vmax=0.5)
    axes[0, 0].set_title(f'Real ΔNDVI (Mid - Pre)\nRange: [{np.nanmin(delta_ndvi):.3f}, {np.nanmax(delta_ndvi):.3f}]')
    axes[0, 0].set_xlabel('X (pixels)')
    axes[0, 0].set_ylabel('Y (pixels)')
    plt.colorbar(im1, ax=axes[0, 0], label='ΔNDVI')
    
    # 2. Real binary change map
    im2 = axes[0, 1].imshow(change_map, cmap='RdYlBu', vmin=0, vmax=1)
    axes[0, 1].set_title(f'Real Binary Change Map\nThreshold: {optimal_threshold:.3f}')
    axes[0, 1].set_xlabel('X (pixels)')
    axes[0, 1].set_ylabel('Y (pixels)')
    plt.colorbar(im2, ax=axes[0, 1], label='Change (1=Yes, 0=No)')
    
    # 3. Validation points overlay
    im3 = axes[0, 2].imshow(delta_ndvi, cmap='RdYlGn', vmin=-0.5, vmax=0.5, alpha=0.7)
    
    # Plot validation points
    for idx, row in validation_gdf.iterrows():
        if hasattr(row['geometry'], 'x'):
            lon, lat = row['geometry'].x, row['geometry'].y
        else:
            lon, lat = row['lon'], row['lat']
        
        # Convert to pixel coordinates
        from rasterio.transform import rowcol
        row_idx, col = rowcol(transform, lon, lat)
        
        if (0 <= row_idx < delta_ndvi.shape[0] and 0 <= col < delta_ndvi.shape[1]):
            color = 'red' if row['ground_truth'] == 1 else 'blue'
            axes[0, 2].plot(col, row_idx, 'o', color=color, markersize=6, alpha=0.8)
    
    axes[0, 2].set_title(f'Real ΔNDVI with Validation Points\n({len(validation_gdf)} points)')
    axes[0, 2].set_xlabel('X (pixels)')
    axes[0, 2].set_ylabel('Y (pixels)')
    
    # Add legend for validation points
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', alpha=0.8, label='Change'),
                      Patch(facecolor='blue', alpha=0.8, label='No Change')]
    axes[0, 2].legend(handles=legend_elements, loc='upper right')
    
    # 4. Threshold optimization results
    axes[1, 0].plot(results_df['threshold'], results_df['F1'], 'b-', label='F1 Score', linewidth=2)
    axes[1, 0].plot(results_df['threshold'], results_df['Producer_Accuracy'], 'g--', label='Producer Accuracy', linewidth=2)
    axes[1, 0].plot(results_df['threshold'], results_df['User_Accuracy'], 'r--', label='User Accuracy', linewidth=2)
    axes[1, 0].axvline(optimal_threshold, color='red', linestyle=':', alpha=0.7, label=f'Optimal: {optimal_threshold:.3f}')
    axes[1, 0].set_xlabel('ΔNDVI Threshold')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_title('Real Threshold Optimization')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Confusion matrix
    tp = np.sum((pixel_values < optimal_threshold) & (ground_truth == 1))
    fp = np.sum((pixel_values < optimal_threshold) & (ground_truth == 0))
    tn = np.sum((pixel_values >= optimal_threshold) & (ground_truth == 0))
    fn = np.sum((pixel_values >= optimal_threshold) & (ground_truth == 1))
    
    confusion_matrix = np.array([[tn, fp], [fn, tp]])
    im5 = axes[1, 1].imshow(confusion_matrix, cmap='Blues', vmin=0, vmax=max(tn, fp, fn, tp))
    axes[1, 1].set_title('Real Confusion Matrix')
    axes[1, 1].set_xlabel('Predicted')
    axes[1, 1].set_ylabel('Actual')
    
    # Add annotations
    for i in range(2):
        for j in range(2):
            axes[1, 1].text(j, i, confusion_matrix[i, j], ha='center', va='center', 
                           fontsize=14, fontweight='bold')
    
    # Add labels
    axes[1, 1].set_xticks([0, 1])
    axes[1, 1].set_yticks([0, 1])
    axes[1, 1].set_xticklabels(['No Change', 'Change'])
    axes[1, 1].set_yticklabels(['No Change', 'Change'])
    
    # 6. Pixel value distribution
    change_pixels = pixel_values[ground_truth == 1]
    no_change_pixels = pixel_values[ground_truth == 0]
    
    axes[1, 2].hist(no_change_pixels, bins=20, alpha=0.7, color='blue', label='No Change', density=True)
    axes[1, 2].hist(change_pixels, bins=20, alpha=0.7, color='red', label='Change', density=True)
    axes[1, 2].axvline(optimal_threshold, color='green', linestyle='--', linewidth=2, label=f'Threshold: {optimal_threshold:.3f}')
    axes[1, 2].set_xlabel('ΔNDVI Pixel Value')
    axes[1, 2].set_ylabel('Density')
    axes[1, 2].set_title('Pixel Value Distribution at Validation Points')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/task3_real_accuracy_assessment.png', dpi=300, bbox_inches='tight')
    plt.show()

print("✅ Real Task 3 execution workflow loaded!")
print("Usage: results = execute_real_task3_workflow(task1_real_results)")
