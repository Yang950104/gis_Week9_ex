# Complete Real Data Workflow - Final Version with Fixed Variable Passing
import numpy as np
import matplotlib.pyplot as plt
import os

def execute_complete_real_workflow():
    """
    Execute complete workflow with real Sentinel-2 data:
    Task 1: Spectral analysis with real data
    Task 2: Threshold optimization
    Task 3: Accuracy assessment
    Task 4: Confidence map and phantom water analysis
    
    Returns:
        Dictionary with all results
    """
    print("=" * 80)
    print("COMPLETE REAL DATA WORKFLOW")
    print("Tasks 1, 2, 3, 4 with Real Sentinel-2 Data")
    print("=" * 80)
    
    try:
        # Step 1: Execute Task 1 with real data
        print("\nStep 1: Task 1 - Real Sentinel-2 Data")
        print("-" * 60)
        
        # Check if task 1 has been executed
        if 'task1_real_results' not in globals():
            print("task1_real_results not found. Please execute Task 1 first.")
            print("Run: task1_real_results = execute_task1_with_real_data()")
            return None
        
        task1_real_results = globals()['task1_real_results']
        print("Task 1 completed successfully")
        
        # Step 2: Execute Task 2 with real data
        print("\nStep 2: Task 2 - Threshold Optimization")
        print("-" * 60)
        
        # Use real validation points
        exec(open('fix_validation_week9.py').read())
        validation_gdf = load_validation_points_fixed()
        print("Loaded validation points: " + str(len(validation_gdf)))
        
        # Get real ΔNDVI for threshold optimization
        delta_ndvi = task1_real_results['masked_differences']['delta_NDVI_mid_pre']
        
        # Create transform for validation points
        from rasterio.transform import from_bounds
        transform = from_bounds(*MATAIAN_BBOX, delta_ndvi.shape[1], delta_ndvi.shape[0])
        
        # Perform threshold optimization
        thresholds = np.linspace(-0.1, -0.5, 20)
        results = []
        
        for threshold in thresholds:
            # Extract pixel values at validation points
            pixel_values, ground_truth = extract_pixel_values_at_validation_points(
                delta_ndvi, validation_gdf, transform
            )
            
            # Calculate confusion matrix
            predictions = (pixel_values < threshold).astype(int)
            
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
                'Producer_Accuracy': recall,
                'User_Accuracy': precision,
                'Overall_Accuracy': accuracy,
                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn
            })
        
        # Find optimal threshold
        import pandas as pd
        results_df = pd.DataFrame(results)
        optimal_idx = results_df['F1'].idxmax()
        optimal_threshold = results_df.loc[optimal_idx, 'threshold']
        optimal_metrics = results_df.loc[optimal_idx]
        
        print("Task 2 completed successfully")
        print("Optimal threshold: " + str(optimal_threshold))
        print("F1-Score: " + str(optimal_metrics['F1']))
        
        # Step 3: Execute Task 3 with real data
        print("\nStep 3: Task 3 - Accuracy Assessment")
        print("-" * 60)
        
        exec(open('real_task3_execution.py').read())
        task3_results = execute_real_task3_workflow(task1_real_results)
        
        if task3_results:
            print("Task 3 completed successfully")
            print("F1-Score: " + str(task3_results['f1_score']))
        else:
            print("Task 3 failed")
        
        # Step 4: Execute Task 4 with real data
        print("\nStep 4: Task 4 - Confidence Map & Water Analysis")
        print("-" * 60)
        
        exec(open('real_task4_fixed.py').read())
        task4_results = execute_real_task4(task1_real_results, optimal_threshold)
        
        if task4_results:
            print("Task 4 completed successfully")
            print("High confidence area: " + str(task4_results['zone_statistics']['High Confidence']['area_km2']) + " km²")
        else:
            print("Task 4 failed")
        
        # Step 5: Execute Task 5 with real data
        print("\nStep 5: Task 5 - Captain's Log")
        print("-" * 60)
        
        exec(open('real_task5_execution.py').read())
        task5_results = create_real_captains_log(task1_real_results, 
                                                   {'optimal_threshold': optimal_threshold, 'F1': optimal_metrics['F1']}, 
                                                   task3_results, 
                                                   task4_results)
        
        if task5_results:
            print("Task 5 completed successfully")
            print("High confidence area: " + str(task5_results['change_detection_analysis']['spatial_extent']['high_confidence_area']) + " km²")
        else:
            print("Task 5 failed")
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPLETE WORKFLOW SUMMARY")
        print("=" * 80)
        print("All tasks completed with real Sentinel-2 data")
        print("Optimal threshold: " + str(optimal_threshold))
        print("Task 3 F1-Score: " + str(task3_results['f1_score'] if task3_results else 'N/A'))
        print("Task 4 High confidence area: " + str(task4_results['zone_statistics']['High Confidence']['area_km2'] if task4_results else 'N/A') + " km²")
        print("Task 5 High confidence area: " + str(task5_results['change_detection_analysis']['spatial_extent']['high_confidence_area']) + " km²")
        
        return {
            'task1_results': task1_real_results,
            'task2_results': {
                'thresholds_df': results_df,
                'optimal_threshold': optimal_threshold,
                'optimal_metrics': optimal_metrics
            },
            'task3_results': task3_results,
            'task4_results': task4_results,
            'task5_results': task5_results,
            'summary': {
                'data_type': 'real_sentinel2',
                'optimal_threshold': optimal_threshold,
                'task3_f1_score': task3_results['f1_score'] if task3_results else None,
                'task4_high_confidence_area': task4_results['zone_statistics']['High Confidence']['area_km2'] if task4_results else None,
                'task5_high_confidence_area': task5_results['change_detection_analysis']['spatial_extent']['high_confidence_area']
            }
        }
        
    except Exception as e:
        print("Error in complete workflow: " + str(e))
        import traceback
        traceback.print_exc()
        return None

print("Complete Real Data Workflow loaded!")
print("Usage: results = execute_complete_real_workflow()")
print("\nNote: Make sure Task 1 has been executed first:")
print("task1_real_results = execute_task1_with_real_data()")
print("results = execute_complete_real_workflow()")
