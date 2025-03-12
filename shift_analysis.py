#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shift and pricing analysis for Clipboard Health marketplace
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import scipy.stats as stats
import statsmodels.api as sm
from core import COLORS, PLOT_DIR, TABLE_DIR, TIME_ANALYSIS_DIR


def price_sensitivity_analysis(df):
    """Analyze how claim rates vary with pay rates."""
    print("Analyzing price sensitivity...")
    
    # Create rate buckets
    bucket_size = 5  # $5 increments
    df['rate_bucket'] = (df['rate'] // bucket_size) * bucket_size
    
    # Calculate claim rates by rate bucket
    rate_sensitivity = df.groupby('rate_bucket').agg(
        view_count=('shift_id', 'count'),
        claim_count=('claimed', 'sum'),
        no_show_count=('is_ncns', 'sum')
    ).reset_index()
    
    rate_sensitivity['claim_rate'] = rate_sensitivity['claim_count'] / rate_sensitivity['view_count']
    rate_sensitivity['no_show_rate'] = rate_sensitivity['no_show_count'] / rate_sensitivity['claim_count']
    
    # Add labels for the chart
    rate_sensitivity['rate_label'] = rate_sensitivity['rate_bucket'].apply(lambda x: f'${x}-{x+bucket_size}')
    
    # Plot claim rate by price bucket
    plt.figure(figsize=(14, 8))
    sns.barplot(x='rate_label', y='claim_rate', data=rate_sensitivity, color=COLORS['primary'])
    
    plt.title('Claim Rate by Pay Rate Range')
    plt.xlabel('Pay Rate Range')
    plt.ylabel('Claim Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'pay_rate_sensitivity.png', dpi=300)
    plt.close()
    
    # Plot no-show rate by price bucket
    plt.figure(figsize=(14, 8))
    sns.barplot(x='rate_label', y='no_show_rate', data=rate_sensitivity, color=COLORS['danger'])
    
    plt.title('No-Show Rate by Pay Rate Range')
    plt.xlabel('Pay Rate Range')
    plt.ylabel('No-Show Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'noshow_by_pay_rate.png', dpi=300)
    plt.close()
    
    # Save the rate sensitivity data
    rate_sensitivity.to_csv(TABLE_DIR / 'noshow_by_pay_rate.csv', index=False)
    
    # Regression analysis to find inflection points
    if len(rate_sensitivity) > 5:  # Need enough points for regression
        try:
            # Prepare data for regression
            X = rate_sensitivity['rate_bucket'].values.reshape(-1, 1)
            y = rate_sensitivity['claim_rate'].values
            
            # Add constant
            X_const = sm.add_constant(X)
            
            # Linear regression model
            model = sm.OLS(y, X_const)
            results = model.fit()
            
            # Plot regression line
            plt.figure(figsize=(10, 8))
            plt.scatter(rate_sensitivity['rate_bucket'], rate_sensitivity['claim_rate'], 
                       color=COLORS['primary'], alpha=0.7)
            
            # Generate prediction line
            x_range = np.linspace(rate_sensitivity['rate_bucket'].min(), 
                                 rate_sensitivity['rate_bucket'].max(), 100)
            X_pred = sm.add_constant(x_range.reshape(-1, 1))
            y_pred = results.predict(X_pred)
            
            plt.plot(x_range, y_pred, color=COLORS['secondary'], linewidth=2)
            
            plt.title('Pay Rate Regression Analysis')
            plt.xlabel('Pay Rate ($)')
            plt.ylabel('Claim Rate')
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'pay_rate_regression.png', dpi=300)
            plt.close()
            
            print(f"Pay rate elasticity coefficient: {results.params[1]:.4f}")
            print(f"R-squared: {results.rsquared:.4f}")
        except Exception as e:
            print(f"Regression analysis failed: {e}")
    
    return rate_sensitivity


def shift_type_analysis(df):
    """Analyze preferences for different shift types/slots."""
    print("Analyzing shift type preferences...")
    
    if 'slot' not in df.columns:
        print("Slot information not available, skipping shift type analysis")
        return None
    
    # Calculate key metrics by slot
    slot_metrics = df.groupby('slot').agg(
        views=('shift_id', 'count'),
        claims=('claimed', 'sum'),
        completions=('is_verified', 'sum'),
        no_shows=('is_ncns', 'sum'),
        avg_rate=('rate', 'mean')
    ).reset_index()
    
    slot_metrics['claim_rate'] = slot_metrics['claims'] / slot_metrics['views']
    slot_metrics['completion_rate'] = slot_metrics['completions'] / slot_metrics['claims']
    slot_metrics['no_show_rate'] = slot_metrics['no_shows'] / slot_metrics['claims']
    
    # Plot claim rate by slot
    plt.figure(figsize=(10, 8))
    sns.barplot(x='slot', y='claim_rate', data=slot_metrics, palette='viridis')
    
    plt.title('Claim Rate by Shift Slot')
    plt.xlabel('Shift Slot')
    plt.ylabel('Claim Rate')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'claim_rate_by_slot.png', dpi=300)
    plt.close()
    
    # Plot no-show rate by slot
    plt.figure(figsize=(10, 8))
    sns.barplot(x='slot', y='no_show_rate', data=slot_metrics, color=COLORS['danger'])
    
    plt.title('No-Show Rate by Shift Slot')
    plt.xlabel('Shift Slot')
    plt.ylabel('No-Show Rate')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'noshow_by_slot.png', dpi=300)
    plt.close()
    
    # Plot average rate by slot
    plt.figure(figsize=(10, 8))
    sns.barplot(x='slot', y='avg_rate', data=slot_metrics, color=COLORS['primary'])
    
    plt.title('Average Pay Rate by Shift Slot')
    plt.xlabel('Shift Slot')
    plt.ylabel('Average Pay Rate ($)')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'avg_rate_by_slot.png', dpi=300)
    plt.close()
    
    # Build a confusion matrix of slot preferences
    # For each worker, what percent of their claimed shifts are in each slot?
    worker_slot_prefs = df[df['claimed']].groupby(['worker_id', 'slot']).size().unstack(fill_value=0)
    
    # Convert to percentages
    worker_slot_prefs_pct = worker_slot_prefs.div(worker_slot_prefs.sum(axis=1), axis=0)
    
    # Calculate the average preference across workers
    slot_confusion = worker_slot_prefs_pct.mean().reset_index()
    slot_confusion.columns = ['slot', 'preference_pct']
    
    # Save slot metrics
    slot_metrics.to_csv(TABLE_DIR / 'noshow_by_slot.csv', index=False)
    
    # Plot slot preference confusion matrix
    if len(worker_slot_prefs_pct.columns) > 1:
        plt.figure(figsize=(10, 8))
        confusion_matrix = worker_slot_prefs_pct.T.dot(worker_slot_prefs_pct)
        sns.heatmap(confusion_matrix, annot=True, cmap='viridis', fmt='.2f', cbar=True)
        
        plt.title('Shift Slot Preference Confusion Matrix')
        plt.tight_layout()
        plt.savefig(PLOT_DIR / 'slot_confusion_matrix.png', dpi=300)
        plt.close()
    
    return slot_metrics


def cancellation_analysis(df):
    """Analyze cancellation patterns and their impact."""
    print("Analyzing cancellation behaviors...")
    
    # Calculate days between claim and cancellation
    cancelled_shifts = df[df['canceled']].copy()
    if len(cancelled_shifts) == 0:
        print("No cancellations in dataset, skipping cancellation analysis")
        return None
    
    cancelled_shifts['hours_to_shift'] = (cancelled_shifts['shift_start_at'] - 
                                         cancelled_shifts['canceled_at']).dt.total_seconds() / 3600
    
    # Filter out unreasonable values
    cancelled_shifts = cancelled_shifts[
        (cancelled_shifts['hours_to_shift'] >= 0) & 
        (cancelled_shifts['hours_to_shift'] <= 168)  # 1 week
    ]
    
    # Create hour buckets
    cancelled_shifts['cancel_hours_bucket'] = pd.cut(
        cancelled_shifts['hours_to_shift'],
        bins=[0, 1, 3, 6, 12, 24, 48, 72, 168],
        labels=['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '1-2d', '2-3d', '3-7d']
    )
    
    # Count cancellations by bucket
    cancel_timing = cancelled_shifts['cancel_hours_bucket'].value_counts().sort_index().reset_index()
    cancel_timing.columns = ['time_before_shift', 'cancellation_count']
    
    # Calculate percentage
    cancel_timing['percentage'] = cancel_timing['cancellation_count'] / cancel_timing['cancellation_count'].sum() * 100
    
    # Plot cancellation timing
    plt.figure(figsize=(12, 8))
    sns.barplot(x='time_before_shift', y='percentage', data=cancel_timing, color=COLORS['danger'])
    
    plt.title('When Do Workers Cancel Shifts?')
    plt.xlabel('Time Before Shift Start')
    plt.ylabel('Percentage of Cancellations')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'cancellation_timing.png', dpi=300)
    plt.close()
    
    # Save cancellation timing data
    cancel_timing.to_csv(TABLE_DIR / 'cancellation_timing.csv', index=False)
    
    # Cancellation threshold analysis
    # Group workers by their cancellation rate, then plot retention
    worker_cancel_rates = df.groupby('worker_id').agg(
        claims=('claimed', 'sum'),
        cancellations=('canceled', 'sum')
    )
    
    worker_cancel_rates['cancellation_rate'] = worker_cancel_rates['cancellations'] / worker_cancel_rates['claims']
    worker_cancel_rates = worker_cancel_rates[worker_cancel_rates['claims'] >= 3]  # Minimum sample size
    
    # Create cancellation rate buckets
    bins = [0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
    labels = ['0-5%', '5-10%', '10-20%', '20-30%', '30-50%', '50-100%']
    worker_cancel_rates['cancel_rate_bucket'] = pd.cut(worker_cancel_rates['cancellation_rate'], bins=bins, labels=labels)
    
    # Define a worker as "retained" if they claimed at least one shift in the last 30 days of data
    df_sorted = df.sort_values('shift_start_at')
    last_date = df_sorted['shift_start_at'].max()
    retention_threshold = last_date - pd.Timedelta(days=30)
    
    latest_claims = df[df['claimed']].groupby('worker_id')['shift_start_at'].max()
    retained_workers = latest_claims[latest_claims >= retention_threshold].index
    worker_cancel_rates['retained'] = worker_cancel_rates.index.isin(retained_workers)
    
    # Calculate retention rate by cancellation bucket
    retention_by_cancel = worker_cancel_rates.groupby('cancel_rate_bucket').agg(
        workers=('claims', 'count'),
        retained_count=('retained', 'sum')
    )
    
    retention_by_cancel['retention_rate'] = retention_by_cancel['retained_count'] / retention_by_cancel['workers']
    
    # Plot retention by cancellation rate
    plt.figure(figsize=(12, 8))
    sns.barplot(x=retention_by_cancel.index, y='retention_rate', data=retention_by_cancel, color=COLORS['primary'])
    
    plt.title('Worker Retention by Cancellation Rate')
    plt.xlabel('Cancellation Rate')
    plt.ylabel('Retention Rate')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'retention_by_cancellation.png', dpi=300)
    plt.close()
    
    return cancel_timing, retention_by_cancel


def time_to_decision_analysis(df):
    """Analyze how quickly workers decide to claim shifts and the impact on outcomes."""
    print("Analyzing time-to-decision patterns...")
    
    # Filter to claimed shifts with valid decision times
    decision_df = df[df['claimed'] & ~df['decision_time_minutes'].isna()].copy()
    
    if len(decision_df) == 0:
        print("No valid decision time data, skipping time-to-decision analysis")
        return None
    
    # Create decision time buckets (in minutes)
    bins = [0, 1, 5, 15, 30, 60, 120, 240, 1440]
    labels = ['<1m', '1-5m', '5-15m', '15-30m', '30-60m', '1-2h', '2-4h', '4-24h']
    decision_df['decision_time_bucket'] = pd.cut(decision_df['decision_time_minutes'], bins=bins, labels=labels)
    
    # Count decisions by time bucket
    decision_counts = decision_df['decision_time_bucket'].value_counts().sort_index().reset_index()
    decision_counts.columns = ['decision_time', 'count']
    
    # Calculate percentage
    decision_counts['percentage'] = decision_counts['count'] / decision_counts['count'].sum() * 100
    
    # Plot decision time distribution
    plt.figure(figsize=(12, 8))
    sns.barplot(x='decision_time', y='percentage', data=decision_counts, color=COLORS['primary'])
    
    plt.title('Time to Decision Distribution')
    plt.xlabel('Time Between Viewing and Claiming')
    plt.ylabel('Percentage of Claims')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'time_analysis/decision_time_distribution.png', dpi=300)
    plt.close()
    
    # Save decision time distribution
    decision_counts.to_csv(TABLE_DIR / 'decision_time_distribution.csv', index=False)
    
    # Analyze outcomes by decision time
    decision_outcomes = decision_df.groupby('decision_time_bucket').agg(
        claims=('claimed', 'count'),
        completed=('is_verified', 'sum'),
        cancelled=('canceled', 'sum'),
        no_shows=('is_ncns', 'sum')
    ).reset_index()
    
    decision_outcomes['completion_rate'] = decision_outcomes['completed'] / decision_outcomes['claims']
    decision_outcomes['cancellation_rate'] = decision_outcomes['cancelled'] / decision_outcomes['claims']
    decision_outcomes['no_show_rate'] = decision_outcomes['no_shows'] / decision_outcomes['claims']
    
    # Plot completion rate by decision time
    plt.figure(figsize=(12, 8))
    sns.barplot(x='decision_time_bucket', y='completion_rate', data=decision_outcomes, color=COLORS['success'])
    
    plt.title('Shift Completion Rate by Decision Time')
    plt.xlabel('Time Between Viewing and Claiming')
    plt.ylabel('Completion Rate')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'time_analysis/completion_by_decision_time.png', dpi=300)
    plt.close()
    
    return decision_counts, decision_outcomes


def lead_time_analysis(df):
    """Analyze how lead time affects fill rates."""
    print("Analyzing lead time effects...")
    
    # Filter to shifts with valid lead times
    lead_time_df = df[~df['lead_time_days'].isna()].copy()
    
    if len(lead_time_df) == 0:
        print("No valid lead time data, skipping lead time analysis")
        return None
    
    # Create lead time buckets (in days)
    bins = [0, 1, 2, 3, 5, 7, 14, 30, 60]
    labels = ['Same day', '1 day', '2 days', '3-4 days', '5-6 days', '1-2 weeks', '2-4 weeks', '1-2 months']
    lead_time_df['lead_time_bucket'] = pd.cut(lead_time_df['lead_time_days'], bins=bins, labels=labels)
    
    # Analyze claim and fill rates by lead time
    lead_time_metrics = lead_time_df.groupby('lead_time_bucket').agg(
        shifts=('shift_id', 'nunique'),
        views=('shift_id', 'count'),
        claims=('claimed', 'sum'),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    lead_time_metrics['view_per_shift'] = lead_time_metrics['views'] / lead_time_metrics['shifts']
    lead_time_metrics['claim_rate'] = lead_time_metrics['claims'] / lead_time_metrics['views']
    lead_time_metrics['fill_rate'] = lead_time_metrics['completions'] / lead_time_metrics['shifts']
    
    # Plot fill rate by lead time
    plt.figure(figsize=(12, 8))
    sns.barplot(x='lead_time_bucket', y='fill_rate', data=lead_time_metrics, color=COLORS['primary'])
    
    plt.title('Fill Rate by Lead Time')
    plt.xlabel('Lead Time')
    plt.ylabel('Fill Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'time_analysis/fill_rate_by_lead_time.png', dpi=300)
    plt.close()
    
    # Save lead time metrics
    lead_time_metrics.to_csv(TABLE_DIR / 'fill_rate_by_lead_time.csv', index=False)
    
    return lead_time_metrics


def margin_analysis(df):
    """Analyze relationship between margins and key performance metrics."""
    print("Analyzing margin performance...")
    
    # Ensure margin data is available
    if 'margin' not in df.columns:
        print("Margin data not available, skipping margin analysis")
        return None
    
    # Create margin buckets
    df['margin_bucket'] = pd.cut(
        df['margin'],
        bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0],
        labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
    )
    
    # Calculate key metrics by margin bucket
    margin_metrics = df.groupby('margin_bucket').agg(
        shifts=('shift_id', 'nunique'),
        views=('shift_id', 'count'),
        claims=('claimed', 'sum'),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    margin_metrics['view_per_shift'] = margin_metrics['views'] / margin_metrics['shifts']
    margin_metrics['claim_rate'] = margin_metrics['claims'] / margin_metrics['views']
    margin_metrics['fill_rate'] = margin_metrics['completions'] / margin_metrics['shifts']
    
    # Plot claim rate by margin
    plt.figure(figsize=(12, 8))
    sns.barplot(x='margin_bucket', y='claim_rate', data=margin_metrics, color=COLORS['primary'])
    
    plt.title('Claim Rate by Margin')
    plt.xlabel('Margin')
    plt.ylabel('Claim Rate')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'margin_claim_rate.png', dpi=300)
    plt.close()
    
    # Save margin metrics
    margin_metrics.to_csv(TABLE_DIR / 'margin_performance_metrics.csv', index=False)
    
    return margin_metrics


def shift_value_analysis(df):
    """Analyze how total shift value affects worker behavior."""
    print("Analyzing shift value impacts...")
    
    # Ensure shift value data is available
    if 'shift_value' not in df.columns:
        print("Shift value data not available, skipping shift value analysis")
        return None
    
    # Create shift value buckets
    df['shift_value_bucket'] = pd.cut(
        df['shift_value'],
        bins=[0, 100, 200, 300, 400, 500, 1000, 2000],
        labels=['$0-100', '$100-200', '$200-300', '$300-400', '$400-500', '$500-1000', '$1000+']
    )
    
    # Calculate key metrics by shift value bucket
    value_metrics = df.groupby('shift_value_bucket').agg(
        views=('shift_id', 'count'),
        claims=('claimed', 'sum'),
        completions=('is_verified', 'sum')
    ).reset_index()
    
    value_metrics['claim_rate'] = value_metrics['claims'] / value_metrics['views']
    value_metrics['completion_rate'] = value_metrics['completions'] / value_metrics['claims']
    
    # Plot claim rate by shift value
    plt.figure(figsize=(12, 8))
    sns.barplot(x='shift_value_bucket', y='claim_rate', data=value_metrics, color=COLORS['primary'])
    
    plt.title('Claim Rate by Total Shift Value')
    plt.xlabel('Shift Value')
    plt.ylabel('Claim Rate')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'shift_value_claim_rate.png', dpi=300)
    plt.close()
    
    # Save shift value metrics
    value_metrics.to_csv(TABLE_DIR / 'shift_value_performance.csv', index=False)
    
    return value_metrics


def dynamic_pricing_analysis(df):
    """Analyze dynamic pricing patterns and their impact on claim rates."""
    print("Analyzing dynamic pricing patterns...")
    
    # Identify shifts that have multiple offers with different rates
    if 'rate' not in df.columns or 'shift_id' not in df.columns:
        print("Required columns for dynamic pricing analysis not found")
        return None
    
    # For each shift, calculate the min, max, and range of offered rates
    shift_rates = df.groupby('shift_id')['rate'].agg(['min', 'max', 'count', 'mean', 'std']).reset_index()
    shift_rates['rate_range'] = shift_rates['max'] - shift_rates['min']
    
    # Identify shifts with multiple rates (dynamic pricing)
    dynamic_shifts = shift_rates[shift_rates['rate_range'] > 0]
    
    # Calculate the percentage of shifts with dynamic pricing
    total_shifts = shift_rates.shape[0]
    dynamic_shifts_pct = dynamic_shifts.shape[0] / total_shifts if total_shifts > 0 else 0
    
    print(f"Percentage of shifts with dynamic pricing: {dynamic_shifts_pct:.2%}")
    
    # Skip if no dynamic pricing
    if dynamic_shifts.shape[0] == 0:
        print("No shifts with dynamic pricing found, skipping dynamic pricing analysis")
        return None
    
    # For shifts with dynamic pricing, analyze how rates change over time
    dynamic_shift_ids = dynamic_shifts['shift_id'].unique()
    
    # Sample up to 1000 shifts for detailed time series analysis
    sample_size = min(1000, len(dynamic_shift_ids))
    sample_shifts = np.random.choice(dynamic_shift_ids, size=sample_size, replace=False)
    
    # For each sampled shift, track rate changes over time
    rate_changes = []
    for shift_id in sample_shifts:
        shift_offers = df[df['shift_id'] == shift_id].sort_values('offer_viewed_at')
        
        # Calculate hours until shift start for each offer
        shift_start = shift_offers['shift_start_at'].iloc[0]
        shift_offers['hours_to_start'] = (shift_start - shift_offers['offer_viewed_at']).dt.total_seconds() / 3600
        
        # Get rate and time data
        for _, offer in shift_offers.iterrows():
            rate_changes.append({
                'shift_id': shift_id,
                'hours_to_start': offer['hours_to_start'],
                'rate': offer['rate'],
                'claimed': offer['claimed']
            })
    
    rate_changes_df = pd.DataFrame(rate_changes)
    
    # Create bins for hours to start
    hour_bins = [0, 1, 3, 6, 12, 24, 48, 72, 168, float('inf')]
    hour_labels = ['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '1-2d', '2-3d', '3-7d', '>7d']
    
    rate_changes_df['hours_bin'] = pd.cut(
        rate_changes_df['hours_to_start'],
        bins=hour_bins,
        labels=hour_labels
    )
    
    # Calculate average rate and claim rate by hours to start
    time_vs_rate = rate_changes_df.groupby('hours_bin').agg({
        'rate': 'mean',
        'claimed': 'mean',
        'shift_id': 'count'
    }).reset_index()
    
    time_vs_rate.columns = ['hours_to_start', 'avg_rate', 'claim_rate', 'offer_count']
    
    # Plot rate changes over time
    plt.figure(figsize=(12, 8))
    ax1 = plt.gca()
    
    # Plot average rate
    sns.lineplot(x='hours_to_start', y='avg_rate', data=time_vs_rate, 
                marker='o', color=COLORS['primary'], linewidth=2, markersize=10,
                ax=ax1, label='Avg. Rate')
    
    # Create a second y-axis for claim rate
    ax2 = ax1.twinx()
    sns.lineplot(x='hours_to_start', y='claim_rate', data=time_vs_rate, 
                marker='s', color=COLORS['secondary'], linewidth=2, markersize=10,
                ax=ax2, label='Claim Rate')
    
    # Add labels and title
    ax1.set_xlabel('Hours Until Shift Start')
    ax1.set_ylabel('Average Pay Rate ($)', color=COLORS['primary'])
    ax2.set_ylabel('Claim Rate', color=COLORS['secondary'])
    
    # Add legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.title('Dynamic Pricing: Rate Changes and Claim Rate by Time to Shift Start')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'dynamic_pricing_time_effect.png', dpi=300)
    plt.close()
    
    # Calculate how often rate increases result in claims
    # For each shift, order offers by time and track rate changes
    rate_impact = []
    for shift_id in sample_shifts:
        shift_offers = df[df['shift_id'] == shift_id].sort_values('offer_viewed_at')
        
        prev_rate = None
        for idx, offer in shift_offers.iterrows():
            if prev_rate is not None:
                rate_change = offer['rate'] - prev_rate
                rate_impact.append({
                    'shift_id': shift_id,
                    'rate_change': rate_change,
                    'claimed': offer['claimed']
                })
            prev_rate = offer['rate']
    
    rate_impact_df = pd.DataFrame(rate_impact)
    
    # Create bins for rate changes
    rate_bins = [-float('inf'), -5, -1, 0, 1, 5, float('inf')]
    rate_labels = [
        'Big decrease (>$5)',
        'Medium decrease ($1-$5)',
        'Small decrease (<$1)',
        'Small increase (<$1)',
        'Medium increase ($1-$5)',
        'Big increase (>$5)'
    ]

    rate_impact_df['rate_change_bin'] = pd.cut(
        rate_impact_df['rate_change'],
        bins=rate_bins,
        labels=rate_labels
    )
    
    # Calculate claim rate by rate change
    rate_change_impact = rate_impact_df.groupby('rate_change_bin').agg({
        'claimed': 'mean',
        'shift_id': 'count'
    }).reset_index()
    
    rate_change_impact.columns = ['rate_change', 'claim_rate', 'offer_count']
    
    # Plot claim rate by rate change
    plt.figure(figsize=(14, 8))
    sns.barplot(x='rate_change', y='claim_rate', data=rate_change_impact, palette='viridis')
    
    plt.title('Claim Rate by Rate Change')
    plt.xlabel('Rate Change')
    plt.ylabel('Claim Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'claim_rate_by_rate_change.png', dpi=300)
    plt.close()
    
    # Save dynamic pricing metrics
    time_vs_rate.to_csv(TABLE_DIR / 'dynamic_pricing_time_effect.csv', index=False)
    rate_change_impact.to_csv(TABLE_DIR / 'rate_change_impact.csv', index=False)
    
    return time_vs_rate, rate_change_impact