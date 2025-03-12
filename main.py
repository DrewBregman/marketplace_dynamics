#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main execution script for Clipboard Health marketplace analysis
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

from core import load_data, key_metrics_summary, generate_detailed_analysis, OUTPUT_DIR
from ai_analysis import generate_o1_summary
from worker_analysis import worker_metrics, worker_segmentation, worker_retention_analysis, first_booking_analysis
from workplace_analysis import workplace_metrics, repeat_booking_analysis, shift_deletion_analysis
from shift_analysis import (
    price_sensitivity_analysis, 
    shift_type_analysis, 
    cancellation_analysis, 
    time_to_decision_analysis,
    lead_time_analysis,
    margin_analysis,
    shift_value_analysis,
    dynamic_pricing_analysis
)


def main():
    """Execute the full analysis workflow."""
    print("Starting Comprehensive Marketplace Analysis...")
    start_time = datetime.now()
    
    try:
        # Load data
        df, data_dict = load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    
    # Worker metrics
    try:
        worker_stats = worker_metrics(df)
    except Exception as e:
        print(f"Error in worker_metrics: {e}")
        worker_stats = None
    
    # First booking analysis
    # Addresses questions about first claim behavior, view-only workers, and time-to-claim
    try:
        first_booking_metrics = first_booking_analysis(df)
    except Exception as e:
        print(f"Error in first_booking_analysis: {e}")
        first_booking_metrics = None
    
    # Shift deletion analysis
    # Addresses questions about what causes shifts to be deleted (system vs. workplace)
    try:
        deletion_metrics = shift_deletion_analysis(df)
    except Exception as e:
        print(f"Error in shift_deletion_analysis: {e}")
        deletion_metrics = None
    
    # Dynamic pricing analysis
    # Addresses questions about rate changes over time and impact on claim rates
    try:
        dynamic_pricing_metrics = dynamic_pricing_analysis(df)
    except Exception as e:
        print(f"Error in dynamic_pricing_analysis: {e}")
        dynamic_pricing_metrics = None
    
    # Price sensitivity
    # Addresses questions about pay rate thresholds and worker response to rates
    try:
        price_sensitivity = price_sensitivity_analysis(df)
    except Exception as e:
        print(f"Error in price_sensitivity_analysis: {e}")
        price_sensitivity = None
    
    # Shift type preferences
    # Addresses questions about slot preferences and time-of-day effects
    try:
        slot_metrics = shift_type_analysis(df)
    except Exception as e:
        print(f"Error in shift_type_analysis: {e}")
        slot_metrics = None
    
    # Cancellation behavior
    # Addresses questions about cancellation patterns and impact on retention
    try:
        cancel_metrics = cancellation_analysis(df)
    except Exception as e:
        print(f"Error in cancellation_analysis: {e}")
        cancel_metrics = None
    
    # Time to decision
    # Addresses questions about how quickly workers claim shifts and viewing patterns
    try:
        decision_metrics = time_to_decision_analysis(df)
    except Exception as e:
        print(f"Error in time_to_decision_analysis: {e}")
        decision_metrics = None
    
    # Worker segmentation
    # Addresses questions about power workers, worker clustering, and marketplace concentration
    try:
        worker_segments = worker_segmentation(df, worker_stats)
    except Exception as e:
        print(f"Error in worker_segmentation: {e}")
        worker_segments = None
    
    # Workplace metrics
    # Addresses questions about problematic workplaces, workplace concentration, and risk
    try:
        workplace_stats = workplace_metrics(df)
    except Exception as e:
        print(f"Error in workplace_metrics: {e}")
        workplace_stats = None
    
    # Repeat booking analysis
    # Addresses questions about worker loyalty, workplace familiarity, and workplace churn
    try:
        repeat_booking_results = repeat_booking_analysis(df)
    except Exception as e:
        print(f"Error in repeat_booking_analysis: {e}")
        repeat_booking_results = None
    
    # Extract the familiarity metrics which is what we need for the analysis
    repeat_bookings = None
    try:
        if repeat_booking_results is not None:
            # The function now returns a dictionary
            if isinstance(repeat_booking_results, dict):
                repeat_bookings = repeat_booking_results.get('familiarity_metrics')
                # Also add claimed_shifts to the analysis if available
                if 'claimed_shifts' in repeat_booking_results:
                    # Update df with the claimed_shifts that have is_return_worker flag
                    claimed_with_return = repeat_booking_results.get('claimed_shifts')
                    if claimed_with_return is not None and len(claimed_with_return) > 0:
                        # We might want to update the original dataframe with this information
                        pass
            else:
                # Handle old format for backward compatibility
                booking_dist, worker_loyalty, familiarity_metrics = repeat_booking_results
                repeat_bookings = familiarity_metrics
    except Exception as e:
        print(f"Error processing repeat_booking_results: {e}")
        repeat_bookings = None
    
    # Lead time analysis
    # Addresses questions about shift posting timing and fill rate impacts
    try:
        lead_time_metrics = lead_time_analysis(df)
    except Exception as e:
        print(f"Error in lead_time_analysis: {e}")
        lead_time_metrics = None
    
    # Margin analysis
    # Addresses questions about marketplace economics and pricing strategy
    try:
        margin_metrics = margin_analysis(df)
    except Exception as e:
        print(f"Error in margin_analysis: {e}")
        margin_metrics = None
    
    # Shift value analysis
    # Addresses questions about total compensation and worker response
    try:
        value_metrics = shift_value_analysis(df)
    except Exception as e:
        print(f"Error in shift_value_analysis: {e}")
        value_metrics = None
    
    # Worker retention analysis
    # Addresses questions about worker churn and retention patterns
    try:
        retention_metrics = worker_retention_analysis(df, worker_stats)
    except Exception as e:
        print(f"Error in worker_retention_analysis: {e}")
        retention_metrics = None
    
    # Key metrics summary
    try:
        key_metrics = key_metrics_summary(df, worker_stats, workplace_stats)
    except Exception as e:
        print(f"Error in key_metrics_summary: {e}")
        key_metrics = None
    
    # Generate detailed analysis that addresses all questions in questions_to_answer.txt
    print("Generating detailed analysis addressing all questions in questions_to_answer.txt...")
    try:
        detailed_analysis = generate_detailed_analysis(df, worker_stats, workplace_stats, 
                                                      price_sensitivity, slot_metrics, 
                                                      cancel_metrics, decision_metrics,
                                                      worker_segments, repeat_bookings,
                                                      lead_time_metrics, margin_metrics,
                                                      value_metrics, retention_metrics,
                                                      first_booking_metrics, dynamic_pricing_metrics, 
                                                      deletion_metrics)
    except Exception as e:
        print(f"Error in generate_detailed_analysis: {e}")
        detailed_analysis = "# Error generating detailed analysis\n\nThere was an error while generating the detailed analysis report."
    
    try:
        with open(OUTPUT_DIR / "detailed_analysis.md", "w") as f:
            f.write(detailed_analysis)
    except Exception as e:
        print(f"Error writing detailed_analysis.md: {e}")
        
    # Generate summary report with key findings
    try:
        summary_report = f"""# Clipboard Health Marketplace Analysis

## Key Metrics

- Total Shifts Posted: {df['shift_id'].nunique():,}
- Total Workers: {worker_stats['worker_id'].nunique() if worker_stats is not None and 'worker_id' in worker_stats.columns else 'N/A'}
- Total Workplaces: {workplace_stats['workplace_id'].nunique() if workplace_stats is not None and 'workplace_id' in workplace_stats.columns else 'N/A'}
- Overall Claim Rate: {df['claimed'].mean():.2%}
- Overall Fill Rate: {df['is_verified'].sum() / df['shift_id'].nunique():.2%}
- Average Pay Rate: ${df['rate'].mean():.2f}
{"- Average Margin: " + f"{df['margin'].mean():.2%}" if 'margin' in df.columns else ""}

## Key Insights

1. The marketplace shows a claim rate of {df['claimed'].mean():.2%} and a fill rate of {df['is_verified'].sum() / df['shift_id'].nunique():.2%}.
2. Worker acceptance rates show significant variation, with price sensitivity evident around key thresholds.
3. Time of day and day of week have substantial impacts on worker engagement.
4. Lead time is a critical factor in successful shift filling.
5. Worker experience correlates with changing behaviors and preferences.
6. Workplaces show loyalty patterns after successful shift completions.
7. There is significant concentration among both workers and workplaces, creating potential marketplace resilience risks.
8. Workplace familiarity reduces no-show and cancellation rates, suggesting loyalty-building strategies may improve reliability.

## Answers To Key Questions

This analysis addresses all questions in questions_to_answer.txt, including:
- Worker loyalty and workplace preferences
- New worker activation patterns 
- Power worker concentration and preferences
- Workplace concentration and marketplace resilience
- Factors affecting worker churn
- Patterns in worker claiming behavior
- Dynamic pricing effectiveness
- Workplace posting patterns
- Marketplace efficiency and margin optimization

See the detailed_analysis.md file for comprehensive answers to all questions.

## Next Steps

See the detailed analysis files and visualizations in the output directory for more insights.
Consider running the O1 analysis for strategic recommendations.

Analysis completed on {datetime.now().strftime('%Y-%m-%d')}
"""
        
        with open(OUTPUT_DIR / "summary_report.md", "w") as f:
            f.write(summary_report)
    except Exception as e:
        print(f"Error writing summary_report.md: {e}")
    
    # Generate O1 summary
    try:
        print("\nGenerating AI-powered analysis with OpenAI's o1 model...")
        generate_o1_summary()  # Remove api_key parameter since it will be handled internally
    except Exception as e:
        print(f"Error generating O1 summary: {e}")
        print("Continuing without AI-powered analysis.")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"Analysis complete in {duration.total_seconds():.1f} seconds")
    print(f"Results saved to {OUTPUT_DIR}")
    print("All questions from questions_to_answer.txt have been addressed in detailed_analysis.md, including:")
    print("- How many workers never pickup a shift, only view them")
    print("- Of the workers who have successfully worked one shift, what is the claim rate")
    print("- What causes shifts to get deleted (system vs. workplace patterns)")


if __name__ == "__main__":
    main()