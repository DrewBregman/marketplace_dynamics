#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI-powered analysis module using OpenAI's o1 model
"""

import os
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import openai

load_dotenv()

openai.organization = os.getenv("OPENAI_ORG_ID", "")
openai.api_key = os.getenv("OPENAI_SECRET_KEY", "")

# Output directory - must match core.py
OUTPUT_DIR = Path('output')

def generate_o1_summary(table_dir=None, print_prompts=False):
    """
    Generate AI-powered analysis with OpenAI's o1 model.
    
    This function runs a multi-step analytical process with each step building on previous steps:
    1. Step 1: Analyze market structure and fundamental patterns
    2. Step 2: Analyze marketplace dynamics (without repeating Step 1 findings)
    3. Step 3: Identify key segments (without repeating Step 1-2 findings)
    4. Step 4: Develop strategic recommendations
    5. Further specialized analyses in specific areas
    
    Parameters:
    - table_dir: Path to tables directory (defaults to OUTPUT_DIR / 'tables')
    - print_prompts: Whether to print the prompts sent to the API (for debugging)
    
    Returns:
    - success: Boolean indicating if the analysis was successful
    """
    print("\nGenerating AI-powered analysis using OpenAI's o1 model...")
    
    if table_dir is None:
        table_dir = OUTPUT_DIR / 'tables'
    
    # Load questions from questions_to_answer.txt - note we won't directly use these
    # but we'll keep the function for backward compatibility
    questions = _load_questions()
    
    # Load data tables for analysis
    data_tables = _load_data_tables(table_dir)
    
    # Step 1: Key metrics and patterns
    print("Step 1: Analyzing key metrics and patterns...")
    step1_prompt = _create_step1_prompt(data_tables)
    
    if print_prompts:
        print("\nStep 1 Prompt:")
        print(step1_prompt)
    
    try:
        step1_insights = _call_o1_api(None, step1_prompt)
        _save_markdown(step1_insights, OUTPUT_DIR / "step1_insights.md")
        print("Saved step1_insights.md")
    except Exception as e:
        print(f"Error in Step 1: {e}")
        return False
    
    # Step 2: Marketplace dynamics
    print("Step 2: Analyzing marketplace dynamics...")
    step2_prompt = _create_step2_prompt(data_tables, step1_insights)
    
    if print_prompts:
        print("\nStep 2 Prompt:")
        print(step2_prompt)
    
    try:
        step2_insights = _call_o1_api(None, step2_prompt)
        _save_markdown(step2_insights, OUTPUT_DIR / "step2_insights.md")
        print("Saved step2_insights.md")
    except Exception as e:
        print(f"Error in Step 2: {e}")
        return False
    
    # Step 3: Key segments
    print("Step 3: Identifying key segments...")
    step3_prompt = _create_step3_prompt(data_tables, step1_insights, step2_insights)
    
    if print_prompts:
        print("\nStep 3 Prompt:")
        print(step3_prompt)
    
    try:
        step3_insights = _call_o1_api(None, step3_prompt)
        _save_markdown(step3_insights, OUTPUT_DIR / "step3_insights.md")
        print("Saved step3_insights.md")
    except Exception as e:
        print(f"Error in Step 3: {e}")
        return False
    
    # Step 3+: Examples
    print("Step 3+: Generating segment examples...")
    examples_prompt = _create_examples_prompt(step3_insights)
    
    if print_prompts:
        print("\nExamples Prompt:")
        print(examples_prompt)
    
    try:
        examples = _call_o1_api(None, examples_prompt)
        _save_markdown(examples, OUTPUT_DIR / "step3_examples.md")
        print("Saved step3_examples.md")
    except Exception as e:
        print(f"Error in Step 3+ (Examples): {e}")
        return False
    
    # Step 4: Strategic recommendations
    print("Step 4: Generating strategic recommendations...")
    step4_prompt = _create_step4_prompt(step1_insights, step2_insights, step3_insights)
    
    if print_prompts:
        print("\nStep 4 Prompt:")
        print(step4_prompt)
    
    try:
        step4_insights = _call_o1_api(None, step4_prompt)
        _save_markdown(step4_insights, OUTPUT_DIR / "step4_insights.md")
        print("Saved step4_insights.md")
    except Exception as e:
        print(f"Error in Step 4: {e}")
        return False
    
    # Step 4+: Next steps
    print("Step 4+: Developing next steps...")
    next_steps_prompt = _create_next_steps_prompt(step4_insights)
    
    if print_prompts:
        print("\nNext Steps Prompt:")
        print(next_steps_prompt)
    
    try:
        next_steps = _call_o1_api(None, next_steps_prompt)
        _save_markdown(next_steps, OUTPUT_DIR / "step4_next_steps.md")
        print("Saved step4_next_steps.md")
    except Exception as e:
        print(f"Error in Step 4+ (Next Steps): {e}")
        return False
    
    # Step 5: Executive summary
    print("Step 5: Creating executive summary...")
    exec_summary_prompt = _create_exec_summary_prompt(
        step1_insights, step2_insights, step3_insights, step4_insights, next_steps
    )
    
    if print_prompts:
        print("\nExecutive Summary Prompt:")
        print(exec_summary_prompt)
    
    try:
        exec_summary = _call_o1_api(None, exec_summary_prompt)
        _save_markdown(exec_summary, OUTPUT_DIR / "step5_executive_summary.md")
        print("Saved step5_executive_summary.md")
    except Exception as e:
        print(f"Error in Step 5 (Executive Summary): {e}")
        return False
    
    # Step 5+: Insights
    print("Step 5+: Extracting key insights...")
    insights_prompt = _create_insights_prompt(step1_insights, step2_insights, step3_insights, 
                                           step4_insights, next_steps, exec_summary)
    
    if print_prompts:
        print("\nInsights Prompt:")
        print(insights_prompt)
    
    try:
        insights = _call_o1_api(None, insights_prompt)
        _save_markdown(insights, OUTPUT_DIR / "step5_insights.md")
        print("Saved step5_insights.md")
    except Exception as e:
        print(f"Error in Step 5+ (Insights): {e}")
        return False
    
    # NEW: Worker Journey Analysis
    print("Analyzing worker journey milestones and interventions...")
    worker_journey_prompt = _create_worker_journey_prompt(step1_insights, step2_insights, step3_insights, data_tables)
    
    if print_prompts:
        print("\nWorker Journey Prompt:")
        print(worker_journey_prompt)
    
    try:
        worker_journey = _call_o1_api(None, worker_journey_prompt)
        _save_markdown(worker_journey, OUTPUT_DIR / "worker_journey_analysis.md")
        print("Saved worker_journey_analysis.md")
    except Exception as e:
        print(f"Error in Worker Journey Analysis: {e}")
    
    # NEW: Marketplace Equilibrium Analysis
    print("Analyzing marketplace equilibrium and optimization...")
    equilibrium_prompt = _create_marketplace_equilibrium_prompt(step1_insights, step2_insights, data_tables)
    
    if print_prompts:
        print("\nMarketplace Equilibrium Prompt:")
        print(equilibrium_prompt)
    
    try:
        equilibrium_analysis = _call_o1_api(None, equilibrium_prompt)
        _save_markdown(equilibrium_analysis, OUTPUT_DIR / "marketplace_equilibrium_analysis.md")
        print("Saved marketplace_equilibrium_analysis.md")
    except Exception as e:
        print(f"Error in Marketplace Equilibrium Analysis: {e}")
    
    # NEW: Behavioral Economics Analysis
    print("Analyzing behavioral economics factors...")
    behavioral_prompt = _create_behavioral_economics_prompt(data_tables, step2_insights, step3_insights)
    
    if print_prompts:
        print("\nBehavioral Economics Prompt:")
        print(behavioral_prompt)
    
    try:
        behavioral_analysis = _call_o1_api(None, behavioral_prompt)
        _save_markdown(behavioral_analysis, OUTPUT_DIR / "behavioral_economics_analysis.md")
        print("Saved behavioral_economics_analysis.md")
    except Exception as e:
        print(f"Error in Behavioral Economics Analysis: {e}")
    
    # NEW: Pricing Optimization Analysis
    print("Developing advanced pricing optimization strategies...")
    pricing_prompt = _create_pricing_optimization_prompt(data_tables, step1_insights, step2_insights)
    
    if print_prompts:
        print("\nPricing Optimization Prompt:")
        print(pricing_prompt)
    
    try:
        pricing_analysis = _call_o1_api(None, pricing_prompt)
        _save_markdown(pricing_analysis, OUTPUT_DIR / "pricing_optimization_strategy.md")
        print("Saved pricing_optimization_strategy.md")
    except Exception as e:
        print(f"Error in Pricing Optimization Analysis: {e}")
    
    # NEW: Network Effects Analysis
    print("Analyzing network effects and flywheel dynamics...")
    network_prompt = _create_network_effects_prompt(data_tables, step1_insights, step2_insights)
    
    if print_prompts:
        print("\nNetwork Effects Prompt:")
        print(network_prompt)
    
    try:
        network_analysis = _call_o1_api(None, network_prompt)
        _save_markdown(network_analysis, OUTPUT_DIR / "network_effects_analysis.md")
        print("Saved network_effects_analysis.md")
    except Exception as e:
        print(f"Error in Network Effects Analysis: {e}")
    
    # NEW: Longitudinal Analysis
    print("Analyzing longitudinal trends and patterns...")
    longitudinal_prompt = _create_longitudinal_analysis_prompt(data_tables, step1_insights)
    
    if print_prompts:
        print("\nLongitudinal Analysis Prompt:")
        print(longitudinal_prompt)
    
    try:
        longitudinal_analysis = _call_o1_api(None, longitudinal_prompt)
        _save_markdown(longitudinal_analysis, OUTPUT_DIR / "longitudinal_trend_analysis.md")
        print("Saved longitudinal_trend_analysis.md")
    except Exception as e:
        print(f"Error in Longitudinal Analysis: {e}")
    
    # NEW: Retention Intervention Analysis
    print("Developing targeted retention interventions...")
    retention_prompt = _create_retention_intervention_prompt(data_tables, step2_insights, step3_insights)
    
    if print_prompts:
        print("\nRetention Intervention Prompt:")
        print(retention_prompt)
    
    try:
        retention_analysis = _call_o1_api(None, retention_prompt)
        _save_markdown(retention_analysis, OUTPUT_DIR / "targeted_retention_interventions.md")
        print("Saved targeted_retention_interventions.md")
    except Exception as e:
        print(f"Error in Retention Intervention Analysis: {e}")
    
    # NEW: Cross-Side Matching Optimization
    print("Analyzing cross-side matching optimization...")
    matching_prompt = _create_cross_side_matching_prompt(data_tables, step2_insights, step3_insights)
    
    if print_prompts:
        print("\nCross-Side Matching Prompt:")
        print(matching_prompt)
    
    try:
        matching_analysis = _call_o1_api(None, matching_prompt)
        _save_markdown(matching_analysis, OUTPUT_DIR / "cross_side_matching_optimization.md")
        print("Saved cross_side_matching_optimization.md")
    except Exception as e:
        print(f"Error in Cross-Side Matching Analysis: {e}")
    
    # NEW: Competitive Advantage Analysis
    print("Analyzing sustainable competitive advantages...")
    competitive_prompt = _create_competitive_advantage_prompt(step1_insights, step2_insights, step3_insights, step4_insights)
    
    if print_prompts:
        print("\nCompetitive Advantage Prompt:")
        print(competitive_prompt)
    
    try:
        competitive_analysis = _call_o1_api(None, competitive_prompt)
        _save_markdown(competitive_analysis, OUTPUT_DIR / "sustainable_competitive_advantage.md")
        print("Saved sustainable_competitive_advantage.md")
    except Exception as e:
        print(f"Error in Competitive Advantage Analysis: {e}")
    
    # NEW: Decision Science Framework
    print("Developing decision science frameworks...")
    decision_prompt = _create_decision_science_prompt(data_tables, step1_insights, step2_insights)
    
    if print_prompts:
        print("\nDecision Science Prompt:")
        print(decision_prompt)
    
    try:
        decision_analysis = _call_o1_api(None, decision_prompt)
        _save_markdown(decision_analysis, OUTPUT_DIR / "decision_science_frameworks.md")
        print("Saved decision_science_frameworks.md")
    except Exception as e:
        print(f"Error in Decision Science Analysis: {e}")
    
    # Final combined report
    print("Creating final comprehensive report...")
    try:
        final_insights = _combine_insights({
            "Executive Summary": exec_summary,
            "Key Metrics & Patterns": step1_insights,
            "Marketplace Dynamics": step2_insights,
            "Key Customer Segments": step3_insights,
            "Segment Examples": examples,
            "Strategic Recommendations": step4_insights,
            "Next Steps": next_steps,
            "Key Insights": insights,
            "Worker Journey Analysis": worker_journey,
            "Marketplace Equilibrium": equilibrium_analysis,
            "Behavioral Economics Factors": behavioral_analysis,
            "Pricing Optimization Strategy": pricing_analysis,
            "Network Effects & Flywheel": network_analysis,
            "Longitudinal Trends": longitudinal_analysis,
            "Retention Interventions": retention_analysis,
            "Cross-Side Matching Optimization": matching_analysis,
            "Sustainable Competitive Advantage": competitive_analysis,
            "Decision Science Frameworks": decision_analysis
        })
        _save_markdown(final_insights, OUTPUT_DIR / "final_multi_step_analysis.md")
        print("Saved final_multi_step_analysis.md")
    except Exception as e:
        print(f"Error creating final report: {e}")
        return False
    
    print("\nAI-powered analysis complete. Results saved to the output directory.")
    return True


def _load_questions():
    """Load questions from questions_to_answer.txt file."""
    questions_path = Path('questions_to_answer.txt')
    
    if not questions_path.exists():
        print(f"Warning: {questions_path} not found. Checking in context directory...")
        questions_path = Path('context/questions_to_answer.txt')
    
    if not questions_path.exists():
        print(f"Warning: No questions file found. Using default questions.")
        return [
            "How do worker behaviors differ across different segments?",
            "What factors most influence marketplace performance?",
            "Which strategies could improve fill rates and retention?"
        ]
    
    with open(questions_path, 'r') as f:
        questions = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(questions)} questions from {questions_path}")
    return questions


def _load_data_tables(table_dir):
    """Extract key metrics and insights from data tables.
    
    Important marketplace data rules:
    1. Shift-level metrics are aggregated by shift_id first for proper fill rate calculation
    2. Worker churn is based on a 30-day inactivity period
    3. Offer data is validated to ensure multiple offers represent real price changes
    """
    insights = {}
    validation_report = []
    
    # Get all CSV files
    csv_files = list(Path(table_dir).glob('**/*.csv'))
    print(f"Found {len(csv_files)} CSV files in {table_dir}")
    
    # Key metrics we want to extract
    insights["marketplace_summary"] = []
    insights["worker_metrics"] = []
    insights["workplace_metrics"] = []
    insights["segments"] = []
    insights["timing_patterns"] = []
    insights["price_sensitivity"] = []
    insights["data_quality"] = []  # New category for data quality checks
    
    # Process each table to extract key metrics
    for file_path in csv_files:
        try:
            table_name = file_path.stem
            print(f"Extracting insights from {table_name}...")
            df = pd.read_csv(file_path)
            
            # SHIFT-LEVEL VALIDATION: If raw shift data, validate and properly aggregate by shift_id
            if 'shift_id' in df.columns and ('claimed_at' in df.columns or 'is_verified' in df.columns):
                # Count unique shifts vs. total offers
                unique_shifts = df['shift_id'].nunique()
                total_rows = len(df)
                
                if unique_shifts < total_rows:
                    # Data contains multiple offers per shift - validate and aggregate
                    validation_report.append(f"Found {total_rows} offers for {unique_shifts} unique shifts")
                    
                    # Verify shifts can have multiple workers
                    if 'worker_id' in df.columns:
                        workers_per_shift = df.groupby('shift_id')['worker_id'].nunique()
                        multi_worker_shifts = (workers_per_shift > 1).sum()
                        if multi_worker_shifts > 0:
                            validation_report.append(f"Confirmed {multi_worker_shifts} shifts with multiple workers")
                            insights["data_quality"].append(f"Multiple workers can be assigned to the same shift ({multi_worker_shifts} examples found)")
                    
                    # Perform shift-level aggregation for key metrics
                    shift_agg = df.groupby('shift_id').agg({
                        'claimed_at': lambda x: (~pd.isna(x)).any(),  # Shift was claimed by at least one worker
                        'canceled_at': lambda x: (~pd.isna(x)).any(),  # Shift had at least one cancellation
                        'is_verified': lambda x: x.any(),  # Shift was completed successfully
                        'is_ncns': lambda x: x.any(),  # Shift had at least one no-show
                        'rate': ['mean', 'min', 'max']  # Rate statistics for the shift
                    })
                    
                    if not shift_agg.empty:
                        # Calculate shift-level metrics
                        total_unique_shifts = len(shift_agg)
                        filled_shifts = shift_agg[('claimed_at', '<lambda_0>')].sum()
                        completed_shifts = shift_agg[('is_verified', '<lambda_0>')].sum()
                        
                        # Calculate fill rate based on unique shifts
                        fill_rate = filled_shifts / total_unique_shifts if total_unique_shifts > 0 else 0
                        completion_rate = completed_shifts / filled_shifts if filled_shifts > 0 else 0
                        
                        insights["marketplace_summary"].extend([
                            f"Shift-level metrics (properly aggregated): {filled_shifts}/{total_unique_shifts} shifts filled ({fill_rate:.2%})",
                            f"Shift completion rate: {completion_rate:.2%}"
                        ])
                        
                        # Check for dynamic pricing by analyzing rate variation within shifts
                        rate_variation = shift_agg[('rate', 'max')] - shift_agg[('rate', 'min')]
                        shifts_with_price_changes = (rate_variation > 0).sum()
                        
                        if shifts_with_price_changes > 0:
                            price_change_pct = shifts_with_price_changes / total_unique_shifts
                            avg_price_change = rate_variation[rate_variation > 0].mean()
                            
                            insights["price_sensitivity"].append(
                                f"Dynamic pricing detected in {shifts_with_price_changes} shifts ({price_change_pct:.2%}) with average change of ${avg_price_change:.2f}"
                            )
                            validation_report.append(f"Validated real price changes in {shifts_with_price_changes} shifts")
            
            # CHURN VALIDATION: Verify 30-day churn definition
            if ('churn' in table_name.lower() or 'retention' in table_name.lower()) and 'days' in df.columns:
                # Check for 30-day period in churn/retention calculations
                if 30 in df['days'].values:
                    day30_value = df[df['days'] == 30]['retention_rate'].iloc[0] if 'retention_rate' in df.columns else "present"
                    validation_report.append(f"Confirmed 30-day churn/retention metric: {day30_value}")
                else:
                    validation_report.append("WARNING: 30-day churn/retention period not found in data")
                    insights["data_quality"].append("Churn definition does not appear to use standard 30-day period")
            
            # OFFER VALIDATION: Ensure multiple offers for the same shift are real price changes
            if 'shift_id' in df.columns and 'worker_id' in df.columns and 'rate' in df.columns:
                # Look for duplicate offer patterns (same shift+worker, different rates)
                if len(df) > df.drop_duplicates(['shift_id', 'worker_id']).shape[0]:
                    # Group to find duplicates
                    dupes = df.groupby(['shift_id', 'worker_id']).filter(lambda x: len(x) > 1)
                    
                    if not dupes.empty:
                        # Check if duplicates have different rates (real price changes)
                        dupes_with_price_changes = dupes.groupby(['shift_id', 'worker_id']).filter(
                            lambda x: x['rate'].nunique() > 1
                        )
                        
                        # Potential system duplicates (same rate shown multiple times)
                        potential_system_dupes = len(dupes) - len(dupes_with_price_changes)
                        
                        if len(dupes_with_price_changes) > 0:
                            insights["price_sensitivity"].append(
                                f"Found {len(dupes_with_price_changes)} offers with real price changes visible to workers"
                            )
                        
                        if potential_system_dupes > 0:
                            validation_report.append(
                                f"WARNING: Found {potential_system_dupes} duplicate offers with identical rates (potential system artifacts)"
                            )
                            insights["data_quality"].append(
                                f"Data quality issue: {potential_system_dupes} duplicate offers have identical rates"
                            )
            
            # Extract key metrics from special tables
            if table_name == 'key_metrics':
                # Extract all key metrics directly
                for _, row in df.iterrows():
                    if 'category' in row and 'metric' in row:
                        category = row['category'] if 'category' in row else 'Uncategorized'
                        metric = row['metric'] if 'metric' in row else 'Unknown metric'
                        value = row['formatted_value'] if 'formatted_value' in row else row['value'] if 'value' in row else 'N/A'
                        
                        insights["marketplace_summary"].append(f"{category} - {metric}: {value}")
            
            elif table_name == 'worker_aggregates':
                # Calculate worker summary metrics
                insights["worker_metrics"].extend([
                    f"Total workers: {len(df)}",
                    f"Average claim rate: {df['claim_rate'].mean():.2%}" if 'claim_rate' in df.columns else "",
                    f"Average completion rate: {df['completion_rate'].mean():.2%}" if 'completion_rate' in df.columns else "",
                    f"Average cancellation rate: {df['cancellation_rate'].mean():.2%}" if 'cancellation_rate' in df.columns else ""
                ])
                
                # Check for 30-day churn definition
                if 'churn_window_days' in df.columns:
                    churn_days = df['churn_window_days'].iloc[0] if not df.empty else None
                    if churn_days:
                        if churn_days == 30:
                            validation_report.append(f"Confirmed worker churn uses 30-day definition")
                        else:
                            validation_report.append(f"WARNING: Worker churn uses {churn_days}-day definition, not the standard 30-day")
                            insights["data_quality"].append(f"Non-standard churn definition: {churn_days} days (standard is 30 days)")
                
                # Add power worker metrics if available
                if 'views' in df.columns and 'claims' in df.columns:
                    power_workers = df.sort_values('claims', ascending=False).head(int(len(df) * 0.2))
                    total_claims = df['claims'].sum()
                    power_claims = power_workers['claims'].sum()
                    
                    if total_claims > 0:
                        insights["worker_metrics"].append(f"Top 20% of workers account for {power_claims/total_claims:.2%} of all claims")
            
            elif table_name == 'workplace_aggregates':
                # Calculate workplace summary metrics
                insights["workplace_metrics"].extend([
                    f"Total workplaces: {len(df)}",
                    f"Average fill rate: {df['fill_rate'].mean():.2%}" if 'fill_rate' in df.columns else "",
                    f"Average claim rate: {df['claim_rate'].mean():.2%}" if 'claim_rate' in df.columns else "",
                    f"Average cancellation rate: {df['cancellation_rate'].mean():.2%}" if 'cancellation_rate' in df.columns else ""
                ])
                
                # Validate shift-level metrics are calculated properly
                if 'fill_rate' in df.columns and 'shifts_posted' in df.columns and 'shifts_filled' in df.columns:
                    # Check if fill rate is calculated based on shift-level data
                    calculated_fill_rate = df['shifts_filled'].sum() / df['shifts_posted'].sum() if df['shifts_posted'].sum() > 0 else 0
                    reported_fill_rate = df['fill_rate'].mean()
                    
                    if abs(calculated_fill_rate - reported_fill_rate) > 0.01:  # 1% difference threshold
                        validation_report.append(
                            f"WARNING: Possible fill rate calculation issue. Shift-based: {calculated_fill_rate:.2%} vs. Reported: {reported_fill_rate:.2%}"
                        )
                        insights["data_quality"].append(
                            f"Fill rate calculation validated: shift-based {calculated_fill_rate:.2%}"
                        )
                
                # Add concentration metrics
                if 'shifts_posted' in df.columns:
                    top_workplaces = df.sort_values('shifts_posted', ascending=False).head(int(len(df) * 0.2))
                    total_shifts = df['shifts_posted'].sum()
                    top_shifts = top_workplaces['shifts_posted'].sum()
                    
                    if total_shifts > 0:
                        insights["workplace_metrics"].append(f"Top 20% of workplaces account for {top_shifts/total_shifts:.2%} of all shifts")
            
            elif table_name == 'worker_behavior_segments':
                # Add worker segment information
                if 'segment_name' in df.columns:
                    for _, row in df.iterrows():
                        segment_info = f"Worker segment: {row['segment_name']} - "
                        for col in df.columns:
                            if col not in ['segment_name', 'cluster'] and not pd.isna(row[col]):
                                segment_info += f"{col}: {row[col]}, "
                        insights["segments"].append(segment_info.rstrip(', '))
            
            elif table_name == 'workplace_behavior_segments':
                # Add workplace segment information
                if 'segment_name' in df.columns:
                    for _, row in df.iterrows():
                        segment_info = f"Workplace segment: {row['segment_name']} - "
                        for col in df.columns:
                            if col not in ['segment_name', 'cluster'] and not pd.isna(row[col]):
                                segment_info += f"{col}: {row[col]}, "
                        insights["segments"].append(segment_info.rstrip(', '))
            
            elif table_name == 'worker_concentration_metrics' or table_name == 'workplace_concentration_metrics':
                # Add concentration metrics
                entity_type = "Workers" if "worker" in table_name else "Workplaces"
                for _, row in df.iterrows():
                    bucket = row['worker_bucket'] if 'worker_bucket' in df.columns else row['workplace_bucket'] if 'workplace_bucket' in df.columns else 'Unknown'
                    
                    # Extract key concentration metrics
                    metric_info = f"{entity_type} concentration - {bucket}: "
                    
                    for col in df.columns:
                        if 'pct' in col.lower() and not pd.isna(row[col]):
                            metric_info += f"{col}: {row[col]:.2f}%, "
                    
                    insights["marketplace_summary"].append(metric_info.rstrip(', '))
            
            elif table_name == 'hourly_shift_metrics' or table_name == 'daily_shift_metrics':
                # Extract timing patterns
                time_unit = "hour" if "hourly" in table_name else "day"
                
                if 'claim_rate' in df.columns:
                    best_time = df.loc[df['claim_rate'].idxmax()]
                    worst_time = df.loc[df['claim_rate'].idxmin()]
                    
                    time_label_best = best_time['view_hour'] if 'view_hour' in df.columns else best_time['day_name'] if 'day_name' in df.columns else 'Unknown'
                    time_label_worst = worst_time['view_hour'] if 'view_hour' in df.columns else worst_time['day_name'] if 'day_name' in df.columns else 'Unknown'
                    
                    insights["timing_patterns"].extend([
                        f"Best {time_unit} for claims: {time_label_best} (claim rate: {best_time['claim_rate']:.2%})",
                        f"Worst {time_unit} for claims: {time_label_worst} (claim rate: {worst_time['claim_rate']:.2%})"
                    ])
            
            elif table_name == 'dynamic_pricing_time_effect':
                # Validate and extract pricing patterns over time
                if 'hours_to_start' in df.columns and 'avg_rate' in df.columns:
                    # Check that data represents real price changes
                    if 'num_shifts' in df.columns or 'shift_count' in df.columns:
                        shift_count_col = 'num_shifts' if 'num_shifts' in df.columns else 'shift_count'
                        total_shifts = df[shift_count_col].sum()
                        validation_report.append(f"Dynamic pricing analysis based on {total_shifts} shifts")
                    
                    earliest_time = df.iloc[0]
                    latest_time = df.iloc[-1]
                    
                    rate_change = latest_time['avg_rate'] - earliest_time['avg_rate']
                    pct_change = rate_change / earliest_time['avg_rate'] if earliest_time['avg_rate'] > 0 else 0
                    
                    insights["price_sensitivity"].append(
                        f"Dynamic pricing effect: Rates change by {pct_change:.2%} from {earliest_time['hours_to_start']} to {latest_time['hours_to_start']} before shift start"
                    )
            
            elif table_name == 'rate_change_impact':
                # Extract impact of rate changes
                if 'rate_change' in df.columns and 'claim_rate' in df.columns:
                    for _, row in df.iterrows():
                        insights["price_sensitivity"].append(
                            f"Rate change '{row['rate_change']}' leads to claim rate: {row['claim_rate']:.2%}"
                        )
            
            elif 'retention' in table_name.lower():
                # Extract retention metrics with validation for 30-day definition
                retention_info = f"Retention metrics from {table_name}: "
                
                if 'retention_rate' in df.columns:
                    overall_retention = df['retention_rate'].mean() if len(df) > 0 else 0
                    
                    # Check if this includes 30-day retention
                    has_30day = False
                    if 'period' in df.columns:
                        has_30day = any(p == 30 or str(p).lower() == '30 days' or str(p).lower() == '30-day' for p in df['period'])
                        retention_info += f"Average retention rate: {overall_retention:.2%} (30-day standard: {'Yes' if has_30day else 'No'})"
                    else:
                        retention_info += f"Average retention rate: {overall_retention:.2%}"
                    
                    insights["marketplace_summary"].append(retention_info)
                    
                    if not has_30day and 'period' in df.columns:
                        validation_report.append("WARNING: Retention analysis not using 30-day standard period")
            
            # Add a few more specialized tables
            elif table_name == 'first_claim_metrics':
                for _, row in df.iterrows():
                    insights["worker_metrics"].append(f"{row['metric']}: {row['value']}")
                    
            elif table_name == 'cancellation_timing':
                if 'time_before_shift' in df.columns and 'percentage' in df.columns:
                    most_common = df.loc[df['percentage'].idxmax()]
                    insights["timing_patterns"].append(
                        f"Most common cancellation time: {most_common['time_before_shift']} ({most_common['percentage']:.2f}%)"
                    )
                
            elif table_name == 'problematic_workplaces':
                insights["workplace_metrics"].append(f"Found {len(df)} problematic workplaces with low fill rates")
                
        except Exception as e:
            print(f"Error extracting insights from {file_path}: {e}")
            validation_report.append(f"ERROR: Failed to process {table_name}: {str(e)}")
    
    # Add validation report to marketplace summary 
    if validation_report:
        insights["marketplace_summary"].append("--- Data Validation Report ---")
        for validation in validation_report:
            insights["marketplace_summary"].append(validation)
    
    # Clean up insights - remove empty strings and duplicate entries
    for category in insights:
        insights[category] = [insight for insight in insights[category] if insight.strip()]
        insights[category] = list(dict.fromkeys(insights[category]))  # Remove duplicates while preserving order
    
    print("Extracted key insights from data tables with validation")
    return insights


def _call_o1_api(client, prompt, retries=3, delay=5):
    """Call the OpenAI API with optimized chunking and token management."""
    # Calculate approximate token count (rough estimate: 4 chars = 1 token)
    token_estimate = len(prompt) // 4
    print(f"Estimated token count for prompt: ~{token_estimate}")
    
    # Apply more aggressive chunking if needed
    if token_estimate > 8000:
        print(f"Warning: Prompt is very large. Applying aggressive chunking...")
        prompt = _optimize_prompt_for_tokens(prompt)
        token_estimate = len(prompt) // 4
        print(f"Optimized token count: ~{token_estimate}")
    
    # Fail early if prompt is still too large
    if token_estimate > 15000:
        print(f"Error: Prompt is extremely large even after optimization. This may cause API failures.")
    
    # Use the global openai configuration
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1}: Sending request to OpenAI o1 model...")
            
            # Add max_tokens parameter for better response management
            response = openai.chat.completions.create(
                model="o1",  # Use o1 model specifically
                messages=[
                    {"role": "system", "content": "You are a marketplace data scientist analyzing healthcare staffing data."},
                    {"role": "user", "content": prompt}
                ]
            )
            print(f"Request successful. Received {len(response.choices[0].message.content)} characters in response.")
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e).lower()
            print(f"API error: {e}")
            
            # Handle token-related errors specifically
            if "token" in error_str and "exceed" in error_str:
                print("Detected token limit error. Attempting to reduce prompt size...")
                if attempt < retries - 1:
                    # Reduce prompt size more aggressively
                    prompt = _optimize_prompt_for_tokens(prompt, aggressive=True)
                    print(f"Reduced prompt to ~{len(prompt)//4} tokens.")
            else:
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise Exception(f"Failed after {retries} attempts: {e}")


def _save_markdown(content, output_path):
    """Save content to a markdown file.
    
    Parameters:
    - content: The text content to save
    - output_path: Path where the markdown file should be saved
    """
    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the content to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def _optimize_prompt_for_tokens(prompt, aggressive=False):
    """Optimize prompt to reduce token count while preserving critical information."""
    lines = prompt.split('\n')
    result = []
    
    # Track sections for selective removal
    sections = {
        'tables': [],
        'questions': [],
        'examples': [],
        'instructions': [],
        'data': []
    }
    
    current_section = 'instructions'
    
    # Organize prompt content by section types
    for line in lines:
        # Detect section boundaries
        if '## Table' in line or '## Available Data' in line:
            current_section = 'tables'
        elif '## Question' in line or line.strip().startswith('1. ') or line.strip().startswith('- '):
            current_section = 'questions'
        elif 'Sample data' in line or 'Row ' in line:
            current_section = 'data'
        elif '## Output' in line or '## Format' in line:
            current_section = 'instructions'
        
        sections[current_section].append(line)
    
    # Reduce tokens by section priority
    max_length = 30000 if aggressive else 50000
    
    # Always keep instructions and key elements
    result.extend(sections['instructions'])
    
    # Add questions (limit if aggressive)
    if aggressive:
        # Keep only 2-3 questions
        question_limit = min(len(sections['questions']), 5)
        result.extend(sections['questions'][:question_limit])
    else:
        result.extend(sections['questions'])
    
    # Only include essential table information
    table_limit = 5 if aggressive else 10
    result.extend(sections['tables'][:table_limit])
    
    # Very limited data samples if aggressive
    if aggressive:
        data_lines = []
        for line in sections['data']:
            # Keep only table headers and at most 1-2 sample rows
            if 'Sample data' in line or ('Row 1' in line or 'Columns' in line):
                data_lines.append(line)
        result.extend(data_lines)
    else:
        # Limited data samples
        data_lines = []
        row_count = 0
        for line in sections['data']:
            if 'Row ' in line:
                row_count += 1
                if row_count > 2:  # Limit sample rows
                    continue
            data_lines.append(line)
        result.extend(data_lines)
    
    # Join everything and check length
    optimized = '\n'.join(result)
    
    # Final truncation if still too long
    if len(optimized) > max_length:
        optimized = optimized[:max_length] + "\n\n[Content truncated to fit token limits]"
    
    return optimized


def _create_step1_prompt(data_tables, questions=None):
    """Create prompt for Step 1: Key metrics analysis."""
    prompt = """# Marketplace Analysis Step 1: Market Structure and Network Performance

You are a strategic consultant analyzing a two-sided healthcare staffing marketplace where workers book per diem shifts at healthcare facilities. Your task is to extract meaningful insights about marketplace efficiency, performance bottlenecks, and strategic opportunities.

## Context and Data Rules
This marketplace connects healthcare workers with healthcare facilities for shift-based work. Workers view shift offers in an app, showing location, duration, and pay rate. They can claim shifts, cancel bookings, or facilities can delete shifts. 

IMPORTANT: When analyzing the data, follow these critical rules:
1. Each row in the raw data represents a shift offer (view), not a unique shift. A single shift may have many offers to different workers. All shift-level metrics (fill rate, total shifts posted) must be aggregated by shift_id first.
2. A shift can have multiple workers assigned to it, so don't assume a 1:1 relationship between shifts and workers.
3. Worker churn must be defined using the 30-day standard (a worker is considered churned after 30 days of inactivity).
4. Multiple "offers" for the same shift and worker should be validated to ensure they represent real price changes the worker saw, not system artifacts.

## Your Analysis Task
Conduct a rigorous structural analysis of the marketplace:

1. Market Concentration - Analyze the distribution of activity across workers and workplaces
2. Matching Efficiency - Evaluate how effectively the marketplace connects supply and demand
3. Conversion Funnel - Assess each stage of the pipeline from shift posting to completion
4. Price-Volume Relationships - Identify how pay rates affect key marketplace metrics
5. Marketplace Liquidity - Measure the health of the marketplace in terms of transaction volume and matching speed

Your analysis should focus on discovering actionable insights that identify:
- Structural inefficiencies in the marketplace
- Potential optimization opportunities
- Key performance bottlenecks
- Critical metrics that should be tracked and optimized

## Available Extracted Insights:
"""
    
    # Add data quality insights first if available
    if "data_quality" in data_tables and data_tables["data_quality"]:
        prompt += "\n### Data Quality and Validation\n"
        for insight in data_tables["data_quality"]:
            prompt += f"- {insight}\n"
    
    # Add marketplace summary insights
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        prompt += "\n### Marketplace Summary Metrics\n"
        for insight in data_tables["marketplace_summary"]:
            prompt += f"- {insight}\n"
    
    # Add worker metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n### Worker Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add workplace metrics
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n### Workplace Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add segments
    if "segments" in data_tables and data_tables["segments"]:
        prompt += "\n### Market Segments\n"
        for insight in data_tables["segments"][:5]:  # Limit to 5 segments for brevity
            prompt += f"- {insight}\n"
    
    # Add timing patterns
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        prompt += "\n### Timing Patterns\n"
        for insight in data_tables["timing_patterns"]:
            prompt += f"- {insight}\n"
    
    # Add price sensitivity data
    if "price_sensitivity" in data_tables and data_tables["price_sensitivity"]:
        prompt += "\n### Price Sensitivity Insights\n"
        for insight in data_tables["price_sensitivity"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Analysis Framework
Apply these analytical frameworks to your analysis:

1. Power Law Distribution Analysis - How concentrated is marketplace activity among top participants?
2. Market Clearing Efficiency - How well does supply meet demand across different dimensions (time, location, etc.)?
3. Pareto Principle Validation - Does the 80/20 rule (or similar distribution) apply to this marketplace?
4. Liquidity Analysis - Are there enough participants to ensure consistent matching?
5. Elasticity Modeling - How sensitive are key metrics to changes in price, time, or other factors?
6. Funnel Optimization - Where are the biggest drop-offs in the transaction pipeline?

## Metric Calculation Guidelines
To ensure analytical accuracy:
1. Always use shift-level aggregation when calculating fill rates and other shift metrics
2. Verify that churn and retention metrics use the standard 30-day definition
3. When analyzing price sensitivity, focus on verifiable price changes, not system artifacts
4. Consider that shifts can have multiple workers when analyzing worker-shift relationships

## Output Format
Your response should be in markdown format with the following sections:
1. Data Quality Assessment - Evaluate the reliability of the data and any calculation adjustments made
2. Market Structure and Concentration - Analyze power laws and concentration metrics
3. Matching Efficiency Analysis - Evaluate how well supply meets demand
4. Conversion Funnel Performance - Identify key drop-off points
5. Price-Volume Relationships - Analyze elasticity and dynamic pricing effects
6. Critical Performance Metrics - Highlight the most important KPIs
7. Strategic Opportunities and Risks - Identify actionable insights

For each section, provide quantitative insights, identify patterns, offer strategic implications, and suggest optimization approaches. Prioritize insights that would be most valuable for marketplace operators to understand and act upon."""
    
    return prompt


def _create_step2_prompt(data_tables, step1_insights, questions=None):
    """Create prompt for Step 2: Marketplace dynamics."""
    prompt = """# Marketplace Analysis Step 2: Dynamic Equilibrium and Market Forces

Building on the marketplace structure analysis in Step 1, now examine the dynamic relationships and forces that drive marketplace behavior. Your task is to analyze how different variables interact to create marketplace outcomes.

## Context and Previous Analysis
In two-sided marketplaces, the dynamic interplay between supply and demand creates complex equilibrium patterns. Your analysis should uncover the underlying forces driving these dynamics to enable strategic interventions.

IMPORTANT:
1. DO NOT REPEAT the data quality assessment from Step 1. Instead, focus exclusively on how those data quality factors specifically impact dynamic analysis.
2. REFERENCE but DO NOT RESTATE the market structure findings from Step 1.
3. FOCUS ON NEW INSIGHTS about dynamic patterns, not static structure.

## Your Analysis Task
Analyze these key marketplace dynamics:

1. Supply-Demand Balance - Where and when do supply shortages or surpluses occur? What causes these imbalances?
2. Price Elasticity Patterns - How do different segments respond to price changes? What are the key price thresholds?
3. Temporal and Cyclical Patterns - How do marketplace dynamics change by time of day, day of week, or seasonally?
4. Matching Velocity - What factors speed up or slow down the matching process? How does lead time affect matching outcomes?
5. Marketplace Frictions - What causes cancellations, deletions, or no-shows? How could these frictions be reduced?

Focus on uncovering causal mechanisms and feedback loops, not just correlations. Your insights should help operators understand both what is happening and why.

## Step 1 Insights (Market Structure)
"""
    # Add truncated version of step 1 insights - cut back to reduce redundancy
    prompt += step1_insights[:2500] + ("..." if len(step1_insights) > 2500 else "")
    
    prompt += "\n\n## Dynamics-Related Insights:\n"
    
    # Skip adding data quality insights again to avoid redundancy
    
    # Add price sensitivity data
    if "price_sensitivity" in data_tables and data_tables["price_sensitivity"]:
        prompt += "\n### Price Sensitivity Insights\n"
        for insight in data_tables["price_sensitivity"]:
            prompt += f"- {insight}\n"
    
    # Add timing patterns again (important for dynamics)
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        prompt += "\n### Temporal Patterns\n"
        for insight in data_tables["timing_patterns"]:
            prompt += f"- {insight}\n"
    
    # Add any additional marketplace dynamics
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        prompt += "\n### Additional Market Dynamics\n"
        # Filter for insights related to dynamics
        dynamic_insights = [insight for insight in data_tables["marketplace_summary"] 
                           if any(keyword in insight.lower() for keyword in 
                                 ['change', 'time', 'pattern', 'rate', 'trend', 'demand', 'supply'])]
        for insight in dynamic_insights:
            prompt += f"- {insight}\n"
    
    prompt += """
## Analysis Framework
Apply these analytical frameworks to understand the marketplace dynamics:

1. Dynamic Equilibrium Analysis - How do supply and demand balance over time? What factors create temporary or persistent imbalances?
2. Price Response Functions - How sensitive are different segments to price changes? Are there threshold effects or nonlinear responses?
3. Temporal Pattern Recognition - What recurring patterns exist in the data? How predictable are these patterns?
4. Feedback Loop Identification - What positive and negative feedback loops exist in the marketplace?
5. Friction-Point Mapping - Where do transactions break down? What causes these breakdowns?

## Output Format
Your response should be in markdown format with the following sections:
1. Brief Impact of Data Structure on Dynamic Analysis (MAX 1 PARAGRAPH) - Only explain how data structure specifically affects temporal/dynamic analysis, NOT repeating Step 1's data quality findings
2. Supply-Demand Dynamic Balance
   - Where and when does supply fail to meet demand?
   - What CAUSES these imbalances (beyond static structure)?
   - How could these imbalances be addressed?

3. Price Response Dynamics
   - How do workers respond to different price levels and changes OVER TIME?
   - What price thresholds trigger significant behavior changes?
   - How could dynamic pricing strategies be optimized?

4. Temporal and Cyclical Patterns
   - What daily, weekly, or seasonal patterns exist in marketplace behavior?
   - How predictable are these patterns?
   - How could these patterns be leveraged strategically?

5. Marketplace Velocity and Efficiency
   - How quickly do shifts get filled, and what factors affect speed?
   - What patterns exist in matching velocity across different circumstances?
   - How could velocity be improved?

6. Friction Points and Transaction Failures
   - Where and why do transactions break down OVER TIME?
   - What patterns predict cancellations, no-shows, or deletions?
   - How could these frictions be reduced?

7. Strategic Recommendations for Dynamic Optimization
   - What specific interventions would improve marketplace dynamics?
   - How could these be implemented and measured?

Focus on unique insights about marketplace DYNAMICS that weren't covered in Step 1's structural analysis. Identify causal relationships, feedback loops, and time-dependent patterns."""
    
    return prompt


def _create_step3_prompt(data_tables, step1_insights, step2_insights, questions=None):
    """Create prompt for Step 3: Identifying key segments."""
    prompt = """# Marketplace Analysis Step 3: Key Segments and Target Groups

Building on the structure (Step 1) and dynamics (Step 2) analysis, now identify the most important customer segments and target groups. Your task is to analyze how different groups of workers and workplaces behave and what strategies might be effective for each.

## Context and Previous Analysis
This two-sided marketplace has diverse participants with different needs and behaviors. Understanding these segments is critical for targeted interventions and optimization.

IMPORTANT:
1. DO NOT REPEAT the basic marketplace structure findings from Step 1
2. DO NOT REPEAT the marketplace dynamics findings from Step 2
3. FOCUS EXCLUSIVELY on segment identification, characterization, and strategic implications
4. PRIORITIZE precision and actionability over breadth in your segment definitions

## Your Analysis Task
Identify and analyze key segments across these dimensions:

1. Worker Segments - What distinct groups of workers exist? How do they differ in value and behavior?
2. Workplace Segments - What distinct groups of workplaces exist? How do they differ in value and behavior?
3. Cross-Side Matching Patterns - Which worker segments match best with which workplace segments?
4. Segment-Specific Friction Points - Which segments have the highest rates of problems (cancellations, no-shows, etc.)?
5. Strategic Value Assessment - Which segments are most valuable for long-term marketplace growth?

Focus on finding actionable segments that reveal opportunities for targeted interventions.

## Step 1 & 2 Insights (Reference Only)
"""

    # Add much more truncated versions to avoid repetition
    prompt += "From Step 1 (Market Structure): " + step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    prompt += "\n\nFrom Step 2 (Market Dynamics): " + step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n## Segment-Related Insights:\n"
    
    # Add segments data first
    if "segments" in data_tables and data_tables["segments"]:
        prompt += "\n### Identified Market Segments\n"
        for insight in data_tables["segments"]:
            prompt += f"- {insight}\n"
    
    # Add worker metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n### Worker Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add workplace metrics
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n### Workplace Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Analysis Framework
Apply these analytical frameworks to identify and analyze key segments:

1. Behavioral Segmentation - Group participants by their actions, not just attributes
2. Value-Based Segmentation - Identify high-value, mid-value, and low-value groups
3. Lifecycle Segmentation - Analyze participants at different stages (new, established, declining)
4. Activity Pattern Segmentation - Group by frequency, time, and type of marketplace interaction
5. Problem-Based Segmentation - Identify groups with specific friction points or issues

## Output Format
Your response should be in markdown format with the following sections:

1. Worker Segments (3-5 distinct segments maximum)
   - Concise name and description for each segment (e.g., "High-Value Regulars")
   - Specific quantifiable behavioral characteristics
   - Strategic value and growth potential (high/medium/low with justification)
   - Segment-specific challenges that require intervention

2. Workplace Segments (3-5 distinct segments maximum)
   - Concise name and description for each segment
   - Specific quantifiable behavioral characteristics
   - Strategic value and growth potential (high/medium/low with justification)
   - Segment-specific challenges that require intervention

3. Cross-Side Segment Matching (FOCUS ON THIS SECTION)
   - Which worker segments match best with which workplace segments?
   - Where are the most problematic mismatches occurring?
   - What specific factors create good vs. poor matches?

4. Segment Prioritization Framework
   - Clear rank ordering of segments by strategic value
   - Which 2-3 segments should receive highest-priority attention and why?
   - Which segments represent the greatest growth opportunity?
   - Which segments might be de-prioritized despite volume?

5. Segment-Specific Strategic Approaches
   - For each HIGH-PRIORITY segment (worker and workplace):
     * 2-3 specific intervention recommendations
     * Precise measurable success metrics
     * Implementation considerations

Provide actionable strategic guidance that is SPECIFIC to each segment. Avoid generic recommendations that would apply equally to all segments. Be precise in defining exactly how the marketplace should differently serve each important segment."""

    return prompt


def _create_examples_prompt(step3_insights, questions=None):
    """Create prompt for generating example profiles based on segment analysis."""
    prompt = """# Marketplace Analysis: Segment Examples and Profiles

Based on the segment analysis from Step 3, create illustrative examples and personas for the key segments identified. These examples should bring the segments to life and make them more actionable for product and business teams.

## Your Task
For each major segment identified in the previous analysis, create a specific, detailed example that illustrates:

1. Typical behaviors and patterns
2. Key motivations and pain points
3. Specific interaction examples with the marketplace
4. Strategic approaches to better serve this segment

## Previous Segment Analysis
"""

    # Add step 3 insights
    prompt += step3_insights

    prompt += """
## Output Format
Your response should include specific examples for at least:

1. 2-3 Worker Segment Examples
   - "Worker A" - Give them a descriptive name based on their segment
   - Background and context
   - Typical marketplace behaviors (with specific examples)
   - Key motivations and challenges
   - Current pain points or unmet needs
   - Strategic recommendations for serving this segment better

2. 2-3 Workplace Segment Examples
   - "Workplace X" - Give them a descriptive name based on their segment
   - Background and context
   - Typical marketplace behaviors (with specific examples)
   - Key motivations and challenges
   - Current pain points or unmet needs
   - Strategic recommendations for serving this segment better

3. 1-2 Cross-Side Matching Examples
   - Example of a particularly good or poor match between worker and workplace segments
   - Why this match works well or poorly
   - How the matching could be improved

These examples should be specific and concrete enough that product, operations, and marketing teams could use them to guide decision-making. They should feel like real participants in the marketplace, not abstract categories.

Each example should be clearly connected to the data-driven segments identified in the analysis, not just generic personas."""

    return prompt


def _create_step4_prompt(step1_insights, step2_insights, step3_insights, questions=None):
    """Create prompt for Step 4: Cross-analysis insights and limited recommendations."""
    prompt = """# Marketplace Analysis Step 4: Cross-Analysis Insights and Limited Recommendations

Based on the comprehensive analysis of marketplace structure (Step 1), dynamics (Step 2), and key segments (Step 3), now develop deeper integrated insights with a small set of strategic recommendations. Your primary task is to identify cross-cutting patterns and connections between different aspects of the marketplace, with only a brief section on recommendations.

## Context and Previous Analysis
The healthcare staffing marketplace connects healthcare workers with healthcare facilities for shift-based work. Your analysis should focus on discovering deeper insights across all dimensions of the marketplace data.

IMPORTANT:
1. DO NOT REPEAT analysis from previous steps - focus on NEW insights from cross-analysis
2. SYNTHESIZE findings across all previous steps to discover emergent patterns
3. PRIORITIZE insights that reveal underlying marketplace dynamics
4. Focus 85-90% of your response on INSIGHTS, with only 10-15% on recommendations

## Your Analysis Task
Develop comprehensive cross-analysis insights addressing these key areas:

1. Hidden Connections - What non-obvious relationships exist between different marketplace metrics?
2. Root Causes - What underlying factors explain multiple observed phenomena?
3. System Dynamics - How do different parts of the marketplace interact as a system?
4. Predictive Patterns - What early indicators predict later marketplace behavior?
5. Counter-Intuitive Findings - What surprising or unexpected patterns emerge from the data?
6. Insight Synthesis - How do insights from different steps combine to reveal deeper understanding?

Focus primarily on extracting fascinating, non-obvious patterns from the data rather than on prescribing solutions.

## Previous Analysis Reference
"""

    # Use even shorter versions, primarily focused on key findings not already included
    prompt += "Key structural insights (Step 1): " + step1_insights[:500] + "..."
    prompt += "\n\nKey dynamics insights (Step 2): " + step2_insights[:500] + "..."
    prompt += "\n\nKey segment insights (Step 3): " + step3_insights[:1000] + "..."
    
    prompt += """
## Output Format
Your response should be in markdown format with the following sections:

1. Cross-Cutting Patterns (NEW SECTION)
   - Most significant patterns that emerge when synthesizing all previous analyses
   - Non-obvious relationships between different marketplace metrics
   - System-level dynamics that explain multiple observed phenomena

2. Marketplace Mechanics
   - How different parts of the marketplace influence each other
   - Feedback loops and system dynamics in marketplace behavior
   - Causal relationships between different marketplace events

3. Predictive Indicators
   - Early signals that predict later marketplace outcomes
   - Threshold effects where behavior changes dramatically
   - Leading indicators of marketplace health or dysfunction

4. Segment Interplay
   - How different segments interact with each other
   - Cross-side effects between worker and workplace segments
   - Segment migration patterns and lifecycle insights

5. Marketplace Equilibrium Analysis
   - Forces creating or disrupting marketplace balance
   - Elasticity relationships across different dimensions
   - Supply-demand efficiency insights

6. Strategic Implications (LIMIT TO 10-15% OF TOTAL RESPONSE)
   - Key strategic insights that emerge from the cross-analysis
   - Limited high-impact recommendations focused on core marketplace dynamics
   - Areas where intervention would have the most significant system-wide effects

For each insight, include:
- Exact description of the pattern or relationship
- Supporting evidence from the data analysis
- Why this insight is significant for understanding the marketplace
- How this insight connects to or explains other observations"""

    return prompt


def _create_next_steps_prompt(step4_insights, questions=None):
    """Create prompt for generating research next steps based on insights."""
    prompt = """# Marketplace Analysis: Research and Investigation Next Steps

Based on the cross-analysis insights from Step 4, develop a research and investigation roadmap. Your task is to identify the most important areas for further data analysis, research, and exploration before moving to implementation.

## Your Task
Develop a detailed research plan that:

1. Identifies the most important knowledge gaps revealed by the analysis
2. Prioritizes areas where additional data would be most valuable
3. Suggests hypothesis-driven research to confirm key insights
4. Outlines analytical approaches to deepen understanding
5. Proposes limited experiments to test key assumptions

## Previous Cross-Analysis Insights
"""

    # Add step 4 insights
    prompt += step4_insights

    prompt += """
## Output Format
Your response should be in markdown format with the following sections:

1. Research Priorities
   - Top 3-5 knowledge gaps most worth addressing
   - Rationale for prioritization (impact, feasibility, urgency)
   - How additional research would enhance marketplace understanding

2. Data Collection Plan
   - Additional data points that would be valuable to collect
   - Methods for collecting this data
   - How this data would complement existing analysis

3. Validation Approaches
   - Methodologies to validate key insights from the analysis
   - Statistical or analytical techniques to apply
   - How to determine causality vs. correlation

4. Limited Experiments (MAXIMUM 1/3 of total response)
   - Small-scale, low-risk experiments to test hypotheses
   - Expected outcomes and measurement approach
   - How to interpret different possible results

5. Counter-Hypothesis Testing
   - Alternative explanations for observed patterns
   - Methods to rule out or confirm alternative explanations
   - Critical assumptions that should be questioned

Your research plan should focus primarily on deepening understanding before jumping to solutions. Only the final section should begin to bridge to potential implementations, and it should comprise no more than 15% of your total response."""

    return prompt


def _create_exec_summary_prompt(step1_insights, step2_insights, step3_insights, step4_insights, next_steps, questions=None):
    """Create prompt for generating executive summary focused on insights."""
    prompt = """# Marketplace Analysis: Executive Summary

Create a concise, high-impact executive summary of the comprehensive marketplace analysis. This summary should distill only the most important findings with very limited recommendations for senior leadership.

## Your Task
Create a truly executive-level summary that:

1. Highlights ONLY the critical marketplace insights (max 5-7 total)
2. Focuses on data patterns and their business implications
3. Presents the most fascinating and counter-intuitive discoveries
4. Includes only a brief section on potential strategic directions (10-15% of the content)

IMPORTANT:
1. This is NOT a recap of the entire analysis - be ruthlessly selective
2. Maximize signal-to-noise ratio - every sentence must deliver high value
3. Prioritize fascinating insights over action items
4. Write in executive language with concrete business implications
5. Focus 85-90% on WHAT the data shows, not what to do about it

## Previous Analysis Reference
"""

    # Provide only extremely brief references
    prompt += "All prior analysis steps have been completed. This summary should SYNTHESIZE these insights, not repeat them."
    
    # Reference specific key sections
    prompt += "\n\nRefer to the Cross-Cutting Patterns section from Step 4 to ensure the executive summary highlights the most significant patterns."
    
    prompt += """
## Output Format
Your executive summary must be in a brief, high-impact format with these sections:

1. Market Overview (MAXIMUM 2 paragraphs)
   - Essential context about marketplace state
   - Only the most critical performance metrics
   - The 1-2 most fascinating marketplace dynamics

2. Key Marketplace Insights (EXACTLY 5 bullet points)
   - ONLY the most significant and non-obvious patterns
   - Focus on insights that reveal fundamental marketplace mechanics
   - Each insight should highlight surprising or counter-intuitive findings
   - Include quantification of patterns when possible

3. System Dynamics (MAXIMUM 2 paragraphs)
   - How different marketplace elements interact as a system
   - Critical feedback loops and equilibrium forces
   - Most important causal relationships

4. Strategic Implications (EXACTLY 2 bullet points, LIMIT TO 10-15% OF TOTAL RESPONSE)
   - Key areas where the insights suggest potential action
   - Minimal directional guidance based on the data patterns

5. Future Research (EXACTLY 2 bullet points)
   - Most promising areas for additional data analysis
   - Key questions raised by the current findings

CRITICAL: The entire executive summary MUST fit on a single page when printed. Be ruthlessly concise and focus primarily on fascinating insights rather than recommendations. Use concrete business language, not abstract concepts or technical details."""

    return prompt


def _create_insights_prompt(step1_insights, step2_insights, step3_insights, step4_insights, next_steps, exec_summary, questions=None):
    """Create prompt for extracting key insights across all analyses."""
    prompt = """# Marketplace Analysis: Key Insights Extraction

Extract and synthesize the most important and actionable insights from the comprehensive marketplace analysis. Your task is to identify the most valuable findings that should inform strategic decision-making.

## Your Task
Extract and clearly articulate the most important insights about:

1. Marketplace Structure and Performance
2. Supply-Demand Dynamics
3. Key Customer Segments
4. Critical Pain Points and Opportunities
5. Strategic Priorities

## Previous Analysis
Your insights should synthesize findings from all previous analysis phases:

### Executive Summary
"""

    # Add executive summary
    prompt += exec_summary[:1000] + ("..." if len(exec_summary) > 1000 else "")
    
    prompt += "\n\n### Step 1: Market Structure\n"
    
    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:800] + ("..." if len(step3_insights) > 800 else "")
    
    prompt += "\n\n### Step 4: Strategic Recommendations\n"
    
    # Add truncated version of step 4 insights
    prompt += step4_insights[:800] + ("..." if len(step4_insights) > 800 else "")
    
    prompt += "\n\n### Implementation Next Steps\n"
    
    # Add truncated version of next steps
    prompt += next_steps[:800] + ("..." if len(next_steps) > 800 else "")
    
    prompt += """
## Output Format
Your response should be in markdown format with 15-20 clearly articulated key insights. Each insight should:

1. Be stated clearly and concisely in 1-2 sentences
2. Include supporting evidence or metrics where relevant
3. Explain the strategic importance or implications
4. Connect to potential actions or decisions

Examples of good insights:
- "The marketplace exhibits strong power law dynamics, with the top 20% of workers accounting for 73% of all shift claims, suggesting that retention of these power users should be the highest priority."
- "Worker claim rates are 58% higher when shift pay rates increase by at least $4/hour during the last 24 hours before start time, indicating that dynamic pricing should be more aggressively implemented for hard-to-fill shifts."
- "Workers who experience a cancellation within their first 3 shifts have a 64% higher 30-day churn rate, making cancellation follow-up interventions for new workers a critical retention opportunity."

Your insights should be specific, data-driven, and actionable - not general observations or generic recommendations. Focus on the findings that would be most valuable for strategic decision-making."""

    return prompt


def _combine_insights(insights_dict):
    """Combine all insights into a single comprehensive report."""
    combined = """# Comprehensive Marketplace Analysis

This report synthesizes multiple layers of analysis on the marketplace, from fundamental structure to strategic recommendations and implementation plans.

"""
    
    # Add each section
    for section_title, content in insights_dict.items():
        combined += f"## {section_title}\n\n"
        combined += content + "\n\n"
    
    return combined


def _create_worker_journey_prompt(step1_insights, step2_insights, step3_insights, data_tables, questions=None):
    """Create prompt for worker journey analysis."""
    prompt = """# Worker Journey Analysis: Milestones and Interventions

Analyze the worker journey through the marketplace to identify critical milestones, decision points, and intervention opportunities. Your task is to map the worker lifecycle and recommend targeted interventions at key moments.

## Your Task
Map the worker journey through the marketplace and:

1. Identify critical milestones and decision points
2. Determine where workers are most likely to drop off or disengage
3. Discover what factors most strongly influence worker retention
4. Recommend specific interventions at key journey points

## Previous Analysis
Your analysis should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:800] + ("..." if len(step3_insights) > 800 else "")
    
    prompt += "\n\n### Worker-Specific Insights:\n"
    
    # Add worker metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n#### Worker Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add timing patterns related to workers
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        worker_timing = [i for i in data_tables["timing_patterns"] if "worker" in i.lower() or "claim" in i.lower()]
        if worker_timing:
            prompt += "\n#### Worker Timing Patterns\n"
            for insight in worker_timing:
                prompt += f"- {insight}\n"
    
    prompt += """
## Analysis Framework
Apply these frameworks to analyze the worker journey:

1. Lifecycle Mapping - Identify distinct phases in the worker journey
2. Conversion Analysis - Analyze transition rates between journey stages
3. Behavioral Economics - Identify psychological factors influencing decisions
4. Engagement Scoring - Determine what factors predict higher engagement
5. Retention Modeling - Identify what experiences most impact retention

## Output Format
Your response should be in markdown format with the following sections:

1. Worker Journey Map
   - Key phases in the worker lifecycle
   - Critical milestones and decision points
   - Typical timeframes for each phase
   - Success metrics for each phase

2. Acquisition & Onboarding
   - Key friction points during worker acquisition
   - Critical first experiences that impact retention
   - Recommended interventions to improve onboarding
   - Success metrics for acquisition optimization

3. Engagement & Activity
   - Factors driving regular engagement
   - Warning signs of potential disengagement
   - Recommended interventions to increase activity
   - Segment-specific engagement strategies

4. Retention & Growth
   - Key retention predictors and warning signs
   - Critical experiences that impact churn probability
   - Recommended interventions at retention risk points
   - Strategies for increasing worker lifetime value

5. Resurrection & Win-back
   - Opportunities to re-engage dormant workers
   - Most effective win-back strategies
   - Prioritization framework for resurrection efforts
   - Success metrics for resurrection campaigns

For each journey phase, include:
- Key behavioral metrics and milestones
- Critical intervention points
- Specific recommended interventions
- Expected impact of interventions
- Implementation considerations

Focus on specific, actionable recommendations tied directly to the worker journey analysis."""

    return prompt


def _create_marketplace_equilibrium_prompt(step1_insights, step2_insights, data_tables, questions=None):
    """Create prompt for marketplace equilibrium analysis."""
    prompt = """# Marketplace Equilibrium Analysis: Optimization Opportunities

Analyze the marketplace equilibrium dynamics to identify optimization opportunities. Your task is to determine how the marketplace could better balance supply and demand across different dimensions.

## Your Task
Analyze marketplace equilibrium patterns and:

1. Identify structural supply-demand imbalances
2. Determine pricing mechanisms that could improve balance
3. Discover non-price mechanisms to optimize matching
4. Recommend specific interventions to improve marketplace efficiency

## Previous Analysis
Your analysis should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Equilibrium-Related Insights:\n"
    
    # Add price sensitivity data
    if "price_sensitivity" in data_tables and data_tables["price_sensitivity"]:
        prompt += "\n#### Price Sensitivity Insights\n"
        for insight in data_tables["price_sensitivity"]:
            prompt += f"- {insight}\n"
    
    # Add timing patterns 
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        prompt += "\n#### Temporal Patterns\n"
        for insight in data_tables["timing_patterns"]:
            prompt += f"- {insight}\n"
    
    # Add workplace metrics
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n#### Workplace Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Analysis Framework
Apply these frameworks to analyze marketplace equilibrium:

1. Market Clearing Analysis - Where does supply fail to meet demand?
2. Price Elasticity Modeling - How do price changes affect balance?
3. Temporal Optimization - How could timing strategies improve balance?
4. Friction Reduction - How do marketplace frictions affect equilibrium?
5. Segmentation-Based Balancing - How do different segments affect balance?

## Output Format
Your response should be in markdown format with the following sections:

1. Marketplace Equilibrium Assessment
   - Current state of marketplace balance
   - Key supply-demand imbalances
   - Structural causes of imbalances
   - Economic implications of imbalances

2. Price-Based Optimization Strategies
   - Dynamic pricing recommendations
   - Segment-specific pricing strategies
   - Price threshold identification
   - Implementation considerations

3. Non-Price Balancing Mechanisms
   - Supply growth strategies for underserved areas
   - Demand distribution optimization
   - Matching algorithm improvements
   - User experience enhancements

4. Temporal Optimization Approaches
   - Lead time optimization strategies
   - Time-based incentive structures
   - Predictive demand management
   - Planning horizon improvements

5. Supply Elasticity Strategies
   - How to increase worker responsiveness
   - Surge capacity mechanisms
   - Supply reliability improvements
   - Worker flexibility incentives

6. Integrated Marketplace Optimization Framework
   - Combined pricing and non-pricing strategies
   - Implementation prioritization
   - Expected equilibrium improvements
   - Success metrics and monitoring approach

For each section, provide specific, actionable recommendations based on the marketplace data and previous analysis. Focus on practical strategies that could be implemented to improve overall marketplace efficiency and participant satisfaction."""

    return prompt


def _create_behavioral_economics_prompt(data_tables, step2_insights, step3_insights, questions=None):
    """Create prompt for behavioral economics analysis."""
    prompt = """# Behavioral Economics Analysis: Decision Patterns and Interventions

Analyze marketplace participant behavior through a behavioral economics lens to identify psychological factors influencing decisions and potential nudge strategies. Your task is to understand the cognitive biases and decision patterns affecting marketplace outcomes.

## Your Task
Analyze participant behavior and:

1. Identify key behavioral economics principles at work
2. Determine how cognitive biases affect marketplace decisions
3. Discover opportunities for behavioral interventions or "nudges"
4. Recommend specific behavioral design strategies

## Previous Analysis
Your analysis should build on the previous marketplace insights:

### Step 2: Market Dynamics
"""

    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:800] + ("..." if len(step3_insights) > 800 else "")
    
    prompt += "\n\n### Behavior-Related Insights:\n"
    
    # Add price sensitivity data
    if "price_sensitivity" in data_tables and data_tables["price_sensitivity"]:
        prompt += "\n#### Price Sensitivity Insights\n"
        for insight in data_tables["price_sensitivity"]:
            prompt += f"- {insight}\n"
    
    # Add timing patterns 
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        prompt += "\n#### Behavioral Timing Patterns\n"
        for insight in data_tables["timing_patterns"]:
            prompt += f"- {insight}\n"
    
    # Add segments data
    if "segments" in data_tables and data_tables["segments"]:
        prompt += "\n#### Segment Behaviors\n"
        for insight in data_tables["segments"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Behavioral Economics Framework
Apply these behavioral economics principles to analyze marketplace behavior:

1. Loss Aversion - How do participants respond to perceived losses vs. gains?
2. Hyperbolic Discounting - How do time preferences affect decisions?
3. Social Proof - How do social influences affect marketplace behavior?
4. Choice Architecture - How does option presentation affect decisions?
5. Anchoring Effects - How do reference points influence price perceptions?
6. Status Quo Bias - What factors drive or overcome resistance to change?
7. Scarcity and FOMO - How do perceptions of scarcity influence behavior?
8. Mental Accounting - How do participants categorize and evaluate options?

## Output Format
Your response should be in markdown format with the following sections:

1. Behavioral Economics Assessment
   - Key behavioral principles evident in the marketplace
   - Cognitive biases affecting worker decisions
   - Cognitive biases affecting workplace decisions
   - Behavioral friction points

2. Worker Decision Analysis
   - Claim decision behavioral factors
   - Cancellation decision behavioral factors
   - No-show behavioral factors
   - Opportunity for behavioral interventions

3. Workplace Decision Analysis
   - Shift posting behavioral factors
   - Rate setting behavioral factors
   - Deletion decision behavioral factors
   - Opportunity for behavioral interventions

4. Behavioral "Nudge" Recommendations
   - Specific nudge strategies for workers
   - Specific nudge strategies for workplaces
   - Implementation considerations
   - Ethical considerations and limitations

5. Behavioral UX Design Recommendations
   - Information presentation improvements
   - Default option optimization
   - Feedback mechanism enhancements
   - Social influence integration

6. Behavioral Economics Experimentation Plan
   - Key hypotheses to test
   - A/B testing approach
   - Success metrics
   - Implementation roadmap

For each behavioral principle identified, provide specific examples from the marketplace data, explain how it affects outcomes, and recommend practical interventions to leverage or mitigate the principle as appropriate."""

    return prompt


def _create_pricing_optimization_prompt(data_tables, step1_insights, step2_insights, questions=None):
    """Create prompt for pricing optimization analysis."""
    prompt = """# Pricing Optimization Strategy: Advanced Approaches

Develop comprehensive pricing optimization strategies for the marketplace based on the data analysis. Your task is to recommend specific pricing mechanisms and approaches to improve marketplace outcomes.

## Your Task
Develop advanced pricing strategies that:

1. Optimize for marketplace liquidity and efficiency
2. Address segment-specific price elasticity patterns
3. Balance short-term fill rates with long-term marketplace health
4. Leverage behavioral economics principles

## Previous Analysis
Your strategies should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Pricing-Related Insights:\n"
    
    # Add price sensitivity data
    if "price_sensitivity" in data_tables and data_tables["price_sensitivity"]:
        prompt += "\n#### Price Sensitivity Insights\n"
        for insight in data_tables["price_sensitivity"]:
            prompt += f"- {insight}\n"
    
    # Add marketplace summary
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        pricing_insights = [i for i in data_tables["marketplace_summary"] if "price" in i.lower() or "rate" in i.lower() or "$" in i]
        if pricing_insights:
            prompt += "\n#### Additional Price-Related Metrics\n"
            for insight in pricing_insights:
                prompt += f"- {insight}\n"
    
    prompt += """
## Pricing Framework
Apply these pricing frameworks to develop your recommendations:

1. Value-Based Pricing - How to align prices with perceived value
2. Dynamic Pricing - How to adjust prices based on real-time conditions
3. Segment-Based Pricing - How to optimize pricing for different segments
4. Behavioral Pricing - How to leverage psychological factors
5. Two-Sided Pricing - How to balance incentives across marketplace sides
6. Long-Term Pricing Strategy - How to evolve pricing over time

## Output Format
Your response should be in markdown format with the following sections:

1. Pricing Strategy Assessment
   - Current pricing approach effectiveness
   - Key pricing challenges and opportunities
   - Strategic pricing objectives
   - Pricing levers available

2. Dynamic Pricing Framework
   - Real-time pricing algorithm recommendations
   - Key variables to incorporate in pricing
   - Implementation approach
   - Expected impact on marketplace metrics

3. Segment-Based Pricing Strategies
   - Segment-specific pricing approaches
   - Personalization opportunities
   - Implementation considerations
   - Expected impact by segment

4. Behavioral Pricing Tactics
   - Psychological factors to leverage
   - Display and framing recommendations
   - Anchoring and reference point strategies
   - Testing and optimization approach

5. Economic Incentive Structures
   - Beyond base rates: bonuses, guarantees, etc.
   - When to use different incentive types
   - Implementation considerations
   - Expected impact on marketplace behavior

6. Strategic Pricing Evolution
   - How pricing should evolve over time
   - Market maturity considerations
   - Competitive response planning
   - Long-term pricing vision

For each pricing recommendation, include specific implementation guidance, expected impact, measurement approach, and risk considerations. Your recommendations should be practical, data-driven, and directly tied to the marketplace analysis."""

    return prompt


def _create_network_effects_prompt(data_tables, step1_insights, step2_insights, questions=None):
    """Create prompt for network effects analysis."""
    prompt = """# Network Effects Analysis: Flywheel Dynamics and Growth Leverage

Analyze the marketplace network effects and identify how to strengthen virtuous cycles. Your task is to understand the current network effects, how they could be enhanced, and how they can drive sustainable competitive advantage.

## Your Task
Analyze network dynamics and:

1. Identify current network effects (positive and negative)
2. Determine how to strengthen positive network effects
3. Discover how to mitigate negative network effects
4. Recommend specific strategies to accelerate flywheel dynamics

## Previous Analysis
Your analysis should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Network-Related Insights:\n"
    
    # Add concentration metrics
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        network_insights = [i for i in data_tables["marketplace_summary"] if "concentration" in i.lower() or "top" in i.lower()]
        if network_insights:
            prompt += "\n#### Concentration and Network Metrics\n"
            for insight in network_insights:
                prompt += f"- {insight}\n"
    
    # Add worker and workplace metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n#### Worker Network Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n#### Workplace Network Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Network Effects Framework
Apply these network frameworks to develop your analysis:

1. Direct Network Effects - How value increases with same-side participants
2. Indirect Network Effects - How value increases with cross-side participants
3. Data Network Effects - How data accumulation creates increasing value
4. Flywheel Dynamics - How virtuous cycles create self-reinforcing growth
5. Local vs. Global Network Effects - How geography affects network dynamics
6. Cold Start Solutions - How to overcome initial network effect challenges

## Output Format
Your response should be in markdown format with the following sections:

1. Network Effects Assessment
   - Current network effects strength
   - Key enablers and barriers to network effects
   - Competitive implications of network position
   - Network effect optimization opportunities

2. Worker-Side Network Dynamics
   - How worker concentration affects marketplace value
   - Strategies to strengthen worker-side network effects
   - Critical mass considerations
   - Worker-side growth leverage points

3. Workplace-Side Network Dynamics
   - How workplace concentration affects marketplace value
   - Strategies to strengthen workplace-side network effects
   - Critical mass considerations
   - Workplace-side growth leverage points

4. Cross-Side Network Effects
   - How each side creates value for the other
   - Strategies to strengthen cross-side effects
   - Balancing growth across sides
   - Mitigating cross-side scaling challenges

5. Marketplace Flywheel Model
   - Key components of the virtuous cycle
   - Most leveraged intervention points
   - Acceleration strategies
   - Measurement framework

6. Network Defense Strategy
   - How to create sustainable network advantages
   - Multi-homing mitigations
   - Competitive moats
   - Long-term network vision

For each section, provide specific, actionable recommendations based on the marketplace data and previous analysis. Focus on practical strategies that could be implemented to strengthen network effects and accelerate growth."""

    return prompt


def _create_longitudinal_analysis_prompt(data_tables, step1_insights, questions=None):
    """Create prompt for longitudinal trend analysis."""
    prompt = """# Longitudinal Trend Analysis: Patterns and Projections

Analyze temporal patterns in the marketplace data to identify longitudinal trends and make strategic projections. Your task is to understand how the marketplace has evolved over time and what that suggests for future development.

## Your Task
Analyze temporal patterns and:

1. Identify key trends in marketplace metrics over time
2. Determine leading indicators of marketplace health
3. Discover seasonal or cyclical patterns
4. Project future trends and recommend strategic responses

## Previous Analysis
Your analysis should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:1200] + ("..." if len(step1_insights) > 1200 else "")
    
    prompt += "\n\n### Time-Related Insights:\n"
    
    # Add timing patterns
    if "timing_patterns" in data_tables and data_tables["timing_patterns"]:
        prompt += "\n#### Temporal Patterns\n"
        for insight in data_tables["timing_patterns"]:
            prompt += f"- {insight}\n"
    
    # Add marketplace summary with time elements
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        time_insights = [i for i in data_tables["marketplace_summary"] if any(term in i.lower() for term in ["time", "day", "week", "month", "trend", "growth", "decline", "change"])]
        if time_insights:
            prompt += "\n#### Marketplace Temporal Metrics\n"
            for insight in time_insights:
                prompt += f"- {insight}\n"
    
    prompt += """
## Temporal Analysis Framework
Apply these analytical approaches to develop your analysis:

1. Trend Analysis - Identifying directional changes over time
2. Seasonality Detection - Finding recurring cyclical patterns
3. Cohort Analysis - Tracking how similar groups evolve differently
4. Change-Point Detection - Identifying when significant shifts occurred
5. Leading Indicator Identification - Finding early warning signals
6. Projection Modeling - Estimating future trends

## Output Format
Your response should be in markdown format with the following sections:

1. Longitudinal Trend Assessment
   - Key marketplace metrics over time
   - Major trend patterns identified
   - Significant change points and their causes
   - Overall marketplace trajectory

2. Worker-Side Temporal Patterns
   - Worker acquisition trends
   - Worker engagement evolution
   - Worker retention patterns
   - Worker behavior changes over time

3. Workplace-Side Temporal Patterns
   - Workplace acquisition trends
   - Workplace posting behavior evolution
   - Workplace retention patterns
   - Workplace preference changes over time

4. Seasonal and Cyclical Patterns
   - Day-of-week patterns
   - Monthly or seasonal patterns
   - Event-driven fluctuations
   - Predictability assessment

5. Leading Indicators Framework
   - Early warning metrics for marketplace health
   - Predictive indicators for worker behavior
   - Predictive indicators for workplace behavior
   - Monitoring and response recommendations

6. Future Projection and Recommendations
   - Short-term trend projections (3-6 months)
   - Medium-term trend projections (6-18 months)
   - Strategic responses to projected trends
   - Scenario planning for alternate trajectories

For each section, provide specific, data-driven insights based on the marketplace data and previous analysis. Focus on actionable implications of the trends identified."""

    return prompt


def _create_retention_intervention_prompt(data_tables, step2_insights, step3_insights, questions=None):
    """Create prompt for targeted retention interventions."""
    prompt = """# Targeted Retention Interventions: Reducing Churn and Increasing LTV

Design targeted retention interventions for both sides of the marketplace. Your task is to develop specific strategies to reduce churn, increase repeat usage, and maximize lifetime value.

## Your Task
Develop retention strategies that:

1. Address different causes of churn for different segments
2. Target interventions at high-leverage points in participant lifecycle
3. Optimize for long-term lifetime value, not just short-term retention
4. Balance retention efforts across both sides of the marketplace

## Previous Analysis
Your strategies should build on the previous marketplace insights:

### Step 2: Market Dynamics
"""

    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:800] + ("..." if len(step3_insights) > 800 else "")
    
    prompt += "\n\n### Retention-Related Insights:\n"
    
    # Add retention-related marketplace summary
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        retention_insights = [i for i in data_tables["marketplace_summary"] if any(term in i.lower() for term in ["retention", "churn", "repeat", "loyal", "lifetime", "ltv"])]
        if retention_insights:
            prompt += "\n#### Retention Metrics\n"
            for insight in retention_insights:
                prompt += f"- {insight}\n"
    
    # Add worker metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n#### Worker Retention Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add workplace metrics
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n#### Workplace Retention Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Retention Framework
Apply these retention frameworks to develop your recommendations:

1. Churn Prediction Modeling - Identifying who is at risk and why
2. Lifecycle-Based Interventions - Targeting specific lifecycle stages
3. Experience-Based Retention - Addressing negative experiences
4. Value-Based Retention - Increasing perceived and actual value
5. Segment-Specific Approaches - Tailoring strategies to different groups
6. Cross-Side Retention - Leveraging interdependencies between sides

## Output Format
Your response should be in markdown format with the following sections:

1. Retention Strategy Assessment
   - Current state of marketplace retention
   - Key retention challenges and opportunities
   - Strategic retention objectives
   - Retention levers available

2. Worker Retention Framework
   - Key churn drivers by worker segment
   - Critical intervention points in worker lifecycle
   - Segment-specific worker retention strategies
   - Implementation recommendations and expected impact

3. Workplace Retention Framework
   - Key churn drivers by workplace segment
   - Critical intervention points in workplace lifecycle
   - Segment-specific workplace retention strategies
   - Implementation recommendations and expected impact

4. First 30-Day Experience Optimization
   - Critical first experiences affecting long-term retention
   - Onboarding enhancement recommendations
   - Early warning signals and interventions
   - Success metrics and implementation approach

5. Negative Experience Recovery
   - Key negative experiences driving churn
   - Recovery intervention strategies
   - Proactive vs. reactive approaches
   - Implementation considerations

6. Loyalty and Engagement Programs
   - Structured loyalty program recommendations
   - Engagement-driving mechanisms
   - Gamification and behavioral approaches
   - Implementation roadmap

7. Retention Experimentation Plan
   - Key hypotheses to test
   - A/B testing approach
   - Success metrics
   - Implementation timeline

For each retention recommendation, include specific implementation guidance, expected impact, measurement approach, and risk considerations. Your recommendations should be practical, data-driven, and directly tied to the marketplace analysis."""

    return prompt


def _create_cross_side_matching_prompt(data_tables, step2_insights, step3_insights, questions=None):
    """Create prompt for cross-side matching optimization."""
    prompt = """# Cross-Side Matching Optimization: Improving Marketplace Efficiency

Analyze and optimize the matching process between marketplace sides. Your task is to develop strategies that improve how workers and workplaces find and connect with each other.

## Your Task
Develop matching optimization strategies that:

1. Improve the efficiency of the matching process
2. Increase the quality and relevance of matches
3. Reduce friction in the connection process
4. Balance short-term matching with long-term participant satisfaction

## Previous Analysis
Your strategies should build on the previous marketplace insights:

### Step 2: Market Dynamics
"""

    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:800] + ("..." if len(step3_insights) > 800 else "")
    
    prompt += "\n\n### Matching-Related Insights:\n"
    
    # Add marketplace summary
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        matching_insights = [i for i in data_tables["marketplace_summary"] if any(term in i.lower() for term in ["match", "connect", "fill rate", "claim rate", "recommendation"])]
        if matching_insights:
            prompt += "\n#### Matching Metrics\n"
            for insight in matching_insights:
                prompt += f"- {insight}\n"
    
    # Add worker metrics
    if "worker_metrics" in data_tables and data_tables["worker_metrics"]:
        prompt += "\n#### Worker Matching Metrics\n"
        for insight in data_tables["worker_metrics"]:
            prompt += f"- {insight}\n"
    
    # Add workplace metrics
    if "workplace_metrics" in data_tables and data_tables["workplace_metrics"]:
        prompt += "\n#### Workplace Matching Metrics\n"
        for insight in data_tables["workplace_metrics"]:
            prompt += f"- {insight}\n"
    
    prompt += """
## Matching Optimization Framework
Apply these frameworks to develop your recommendations:

1. Information Asymmetry Reduction - Improving available information for decisions
2. Search and Discovery Enhancement - Making it easier to find relevant options
3. Preference Matching - Better aligning participant preferences
4. Friction Reduction - Streamlining the connection process
5. Matching Algorithm Optimization - Improving how options are presented
6. Reputation and Trust Systems - Building confidence in marketplace matches

## Output Format
Your response should be in markdown format with the following sections:

1. Matching Process Assessment
   - Current state of marketplace matching
   - Key matching challenges and opportunities
   - Strategic matching objectives
   - Matching optimization levers available

2. Information Quality and Transparency
   - Current information gaps and asymmetries
   - Recommendations to improve information quality
   - Transparency enhancements
   - Implementation considerations

3. Search and Discovery Optimization
   - Current search and discovery limitations
   - Recommendations to improve findability
   - Personalization and relevance strategies
   - Implementation approach

4. Preference Matching Enhancements
   - How to better understand participant preferences
   - How to use preferences in matching
   - Preference learning and adaptation
   - Implementation considerations

5. Matching Algorithm Recommendations
   - Current algorithm limitations
   - Specific algorithm improvement recommendations
   - Balancing different matching objectives
   - Implementation and testing approach

6. Reputation and Trust Systems
   - Current trust mechanism limitations
   - Reputation system recommendations
   - Quality signaling improvements
   - Implementation considerations

7. Experimentation and Optimization Plan
   - Key hypotheses to test
   - A/B testing approach
   - Success metrics
   - Implementation timeline

For each matching recommendation, include specific implementation guidance, expected impact, measurement approach, and risk considerations. Your recommendations should be practical, data-driven, and directly tied to the marketplace analysis."""

    return prompt


def _create_competitive_advantage_prompt(step1_insights, step2_insights, step3_insights, step4_insights, questions=None):
    """Create prompt for sustainable competitive advantage analysis."""
    prompt = """# Sustainable Competitive Advantage Analysis: Strategic Positioning

Analyze the marketplace's competitive position and develop strategies for sustainable differentiation. Your task is to identify strategic advantages that could create lasting competitive moats.

## Your Task
Develop competitive strategies that:

1. Identify potential sources of sustainable advantage
2. Determine how to strengthen competitive positioning
3. Discover potential threats and how to mitigate them
4. Recommend specific strategies to build lasting moats

## Previous Analysis
Your strategies should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:600] + ("..." if len(step1_insights) > 600 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:600] + ("..." if len(step2_insights) > 600 else "")
    
    prompt += "\n\n### Step 3: Key Segments\n"
    
    # Add truncated version of step 3 insights
    prompt += step3_insights[:600] + ("..." if len(step3_insights) > 600 else "")
    
    prompt += "\n\n### Step 4: Strategic Recommendations\n"
    
    # Add truncated version of step 4 insights
    prompt += step4_insights[:600] + ("..." if len(step4_insights) > 600 else "")
    
    prompt += """
## Competitive Advantage Framework
Apply these frameworks to develop your analysis:

1. Network Effects - How participant scale creates defensible advantages
2. Data Advantages - How proprietary data creates unique value
3. Switching Costs - How to increase participant loyalty and stickiness
4. Brand and Trust - How reputation creates defensible positioning
5. Operational Excellence - How execution quality creates advantage
6. Innovation Strategy - How continuous improvement maintains advantage

## Output Format
Your response should be in markdown format with the following sections:

1. Competitive Position Assessment
   - Current sources of advantage
   - Vulnerability areas
   - Strategic positioning options
   - Competitive threats

2. Network Effect Advantages
   - Current network effect strength
   - Strategies to strengthen network effects
   - Defensive moat potential
   - Implementation considerations

3. Data and Algorithm Advantages
   - Current data advantages
   - Data strategy recommendations
   - Algorithm differentiation opportunities
   - Implementation approach

4. Switching Cost Strategy
   - Current switching cost assessment
   - Strategies to increase positive lock-in
   - Balancing lock-in with participant satisfaction
   - Implementation considerations

5. Brand and Trust Advantages
   - Current brand position
   - Trust-building strategies
   - Reputation management approach
   - Implementation considerations

6. Execution Excellence Strategy
   - Operational advantage opportunities
   - Quality differentiation approach
   - Process optimization strategy
   - Implementation roadmap

7. Innovation and Adaptation Strategy
   - Key innovation focus areas
   - Continuous improvement approach
   - Experimentation framework
   - Implementation plan

For each competitive strategy, include specific implementation guidance, expected impact, measurement approach, and risk considerations. Your recommendations should be practical, data-driven, and directly tied to the marketplace analysis."""

    return prompt


def _create_decision_science_prompt(data_tables, step1_insights, step2_insights, questions=None):
    """Create prompt for decision science frameworks."""
    prompt = """# Decision Science Frameworks: Optimizing Marketplace Decisions

Develop decision frameworks for key marketplace decisions. Your task is to create structured approaches for making critical decisions across product, pricing, and operations.

## Your Task
Develop decision frameworks that:

1. Guide key strategic and operational decisions
2. Incorporate data-driven insights and metrics
3. Balance different objectives and tradeoffs
4. Provide practical guidance for implementation

## Previous Analysis
Your frameworks should build on the previous marketplace insights:

### Step 1: Market Structure
"""

    # Add truncated version of step 1 insights
    prompt += step1_insights[:800] + ("..." if len(step1_insights) > 800 else "")
    
    prompt += "\n\n### Step 2: Market Dynamics\n"
    
    # Add truncated version of step 2 insights
    prompt += step2_insights[:800] + ("..." if len(step2_insights) > 800 else "")
    
    prompt += "\n\n### Key Marketplace Metrics:\n"
    
    # Add marketplace summary
    if "marketplace_summary" in data_tables and data_tables["marketplace_summary"]:
        prompt += "\n#### Marketplace Key Metrics\n"
        metrics = [i for i in data_tables["marketplace_summary"] if any(term in i.lower() for term in ["rate", "metric", "percentage", "ratio", "average"])]
        for insight in metrics[:10]:  # Limit to top 10 metrics
            prompt += f"- {insight}\n"
    
    prompt += """
## Decision Framework Approach
For each key decision area, develop a framework that includes:

1. Decision Objective - What the decision should optimize for
2. Key Inputs - What data and insights should inform the decision
3. Decision Criteria - How different options should be evaluated
4. Tradeoff Management - How to balance competing objectives
5. Implementation Guide - How to apply the framework in practice

## Output Format
Your response should be in markdown format with frameworks for these key decision areas:

1. Pricing Decisions
   - Base rate determination
   - Dynamic pricing adjustments
   - Incentive structure decisions
   - Segment-specific pricing

2. Supply Growth Decisions
   - Worker acquisition targeting
   - Worker activation strategies
   - Worker retention prioritization
   - Supply balancing across segments

3. Demand Growth Decisions
   - Workplace acquisition targeting
   - Shift volume growth strategies
   - Workplace retention prioritization
   - Demand distribution optimization

4. Product Optimization Decisions
   - Feature prioritization
   - Experience improvement focus
   - Platform policy decisions
   - User experience optimization

5. Operational Decisions
   - Resource allocation
   - Performance intervention triggers
   - Quality management approach
   - Process optimization focus

6. Strategic Initiative Decisions
   - Initiative prioritization framework
   - Investment allocation approach
   - Success measurement criteria
   - Go/no-go decision process

For each decision framework, provide a clear structure that could be directly applied by managers making these decisions. Include specific metrics, thresholds, and evaluation criteria where possible."""

    return prompt