#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workplace-focused marketplace analysis for Clipboard Health
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from core import COLORS, PLOT_DIR, TABLE_DIR


def workplace_metrics(df):
    """Calculate and visualize workplace-related metrics."""
    print("Analyzing workplace metrics...")
    
    # Calculate key metrics by workplace
    workplace_stats = df.groupby('workplace_id').agg(
        shifts_posted=('shift_id', 'nunique'),
        views_received=('shift_id', 'count'),
        shifts_claimed=('claimed', 'sum'),
        shifts_completed=('is_verified', 'sum'),
        shifts_cancelled=('canceled', 'sum'),
        shifts_deleted=('deleted', 'sum'),
        avg_rate=('rate', 'mean'),
        avg_charge_rate=('charge_rate', 'mean'),
        avg_margin=('margin', 'mean')
    ).reset_index()
    
    # Calculate derived metrics
    workplace_stats['view_per_shift'] = workplace_stats['views_received'] / workplace_stats['shifts_posted']
    workplace_stats['claim_rate'] = workplace_stats['shifts_claimed'] / workplace_stats['views_received']
    workplace_stats['fill_rate'] = workplace_stats['shifts_completed'] / workplace_stats['shifts_posted']
    workplace_stats['cancellation_rate'] = workplace_stats['shifts_cancelled'] / workplace_stats['shifts_claimed']
    workplace_stats['deletion_rate'] = workplace_stats['shifts_deleted'] / workplace_stats['shifts_posted']
    
    # Save workplace metrics
    workplace_stats.to_csv(TABLE_DIR / 'workplace_aggregates.csv', index=False)
    
    # Analyze workplace concentration (similar to worker concentration)
    workplace_stats = workplace_stats.sort_values('shifts_posted', ascending=False)
    total_shifts = workplace_stats['shifts_posted'].sum()
    
    # Calculate cumulative percentage of shifts
    workplace_stats['cumulative_shifts'] = workplace_stats['shifts_posted'].cumsum()
    workplace_stats['cumulative_shifts_pct'] = workplace_stats['cumulative_shifts'] / total_shifts * 100
    
    # Identify what percentage of workplaces account for X% of shifts
    thresholds = [50, 71.35, 80, 90, 95]  # Including the specific 71.35% from the question
    workplace_pcts = []
    for threshold in thresholds:
        workplaces_needed = workplace_stats[workplace_stats['cumulative_shifts_pct'] <= threshold].shape[0]
        pct_workplaces_needed = workplaces_needed / workplace_stats.shape[0] * 100
        workplace_pcts.append(pct_workplaces_needed)
        print(f"{threshold}% of shifts are posted by the top {pct_workplaces_needed:.1f}% of workplaces")
    
    # Create workplace concentration dataframe
    concentration_df = pd.DataFrame({
        'shifts_pct': thresholds,
        'workplaces_pct': workplace_pcts
    })
    
    # Plot concentration of shifts
    plt.figure(figsize=(10, 8))
    plt.plot(workplace_stats['cumulative_shifts_pct'], workplace_stats.index / len(workplace_stats) * 100, 
             'b-', linewidth=2, label='Shifts')
    
    # Add reference line for perfect equality
    plt.plot([0, 100], [0, 100], 'k--', linewidth=1, label='Perfect Equality')
    
    # Add markers for key thresholds
    for threshold, workplace_pct in zip(thresholds, workplace_pcts):
        plt.plot(threshold, workplace_pct, 'ro', markersize=8)
        plt.annotate(f"{threshold}% of shifts\nby {workplace_pct:.1f}% of workplaces", 
                    (threshold, workplace_pct), xytext=(10, 0), 
                    textcoords='offset points', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.3))
    
    plt.title('Workplace Shift Concentration')
    plt.xlabel('Cumulative % of Shifts')
    plt.ylabel('Cumulative % of Workplaces')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'workplace_concentration.png', dpi=300)
    plt.close()
    
    # Create buckets of workplaces (top 1%, 1-5%, 5-20%, 20-50%, bottom 50%)
    workplace_count = len(workplace_stats)
    workplace_stats['workplace_rank_pct'] = (workplace_stats.index + 1) / workplace_count * 100
    
    # Define workplace buckets
    bins = [0, 1, 5, 20, 50, 100]
    labels = ['Top 1%', '1-5%', '5-20%', '20-50%', 'Bottom 50%']
    workplace_stats['workplace_bucket'] = pd.cut(workplace_stats['workplace_rank_pct'], bins=bins, labels=labels)
    
    # Calculate metrics for each workplace bucket
    bucket_metrics = workplace_stats.groupby('workplace_bucket').agg({
        'workplace_id': 'count',
        'shifts_posted': 'sum',
        'shifts_claimed': 'sum',
        'shifts_completed': 'sum',
        'shifts_cancelled': 'sum',
        'fill_rate': 'mean',
        'claim_rate': 'mean',
        'avg_rate': 'mean',
        'avg_margin': 'mean'
    }).reset_index()
    
    # Calculate percentages
    bucket_metrics['workplace_pct'] = bucket_metrics['workplace_id'] / workplace_count * 100
    bucket_metrics['shifts_pct'] = bucket_metrics['shifts_posted'] / total_shifts * 100
    
    # Save workplace bucket metrics
    bucket_metrics.to_csv(TABLE_DIR / 'workplace_concentration_metrics.csv', index=False)
    
    # Plot fill rate distribution
    plt.figure(figsize=(12, 8))
    sns.histplot(workplace_stats['fill_rate'], bins=20, kde=True, color=COLORS['primary'])
    
    plt.title('Distribution of Workplace Fill Rates')
    plt.xlabel('Fill Rate (Completed / Posted)')
    plt.ylabel('Number of Workplaces')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'workplace_fill_rate_distribution.png', dpi=300)
    plt.close()
    
    # Identify consistently problematic workplaces (high volume, low fill rate)
    problematic_workplaces = workplace_stats[(workplace_stats['shifts_posted'] >= 10) & 
                                            (workplace_stats['fill_rate'] < 0.5)]
    
    if len(problematic_workplaces) > 0:
        print(f"Found {len(problematic_workplaces)} workplaces with consistently low fill rates (<50%)")
        
        # Analyze why these workplaces have low fill rates
        # Compare their pay rates to the average
        avg_pay_rate = df['rate'].mean()
        problematic_pay = problematic_workplaces['avg_rate'].mean()
        pay_delta_pct = (problematic_pay - avg_pay_rate) / avg_pay_rate * 100
        
        print(f"Average pay rate for problematic workplaces: ${problematic_pay:.2f} " +
              f"({pay_delta_pct:.1f}% {'above' if pay_delta_pct > 0 else 'below'} average)")
        
        # Look at lead times for problematic workplaces
        if 'lead_time_days' in df.columns:
            problematic_ids = problematic_workplaces['workplace_id'].values
            problematic_shifts = df[df['workplace_id'].isin(problematic_ids)]
            
            avg_lead_time = df['lead_time_days'].mean()
            problematic_lead_time = problematic_shifts['lead_time_days'].mean()
            lead_delta_pct = (problematic_lead_time - avg_lead_time) / avg_lead_time * 100
            
            print(f"Average lead time for problematic workplaces: {problematic_lead_time:.1f} days " +
                  f"({lead_delta_pct:.1f}% {'above' if lead_delta_pct > 0 else 'below'} average)")
        
        # Plot the top problematic workplaces
        top_problematic = problematic_workplaces.sort_values('shifts_posted', ascending=False).head(10)
        
        plt.figure(figsize=(12, 8))
        bar_plot = sns.barplot(x='workplace_id', y='fill_rate', data=top_problematic, color=COLORS['danger'])
        
        # Add pay rate labels on top of each bar
        for i, workplace in enumerate(top_problematic.itertuples()):
            bar_plot.text(i, workplace.fill_rate + 0.02, f"${workplace.avg_rate:.0f}/hr", 
                         ha='center', color='black', fontweight='bold')
        
        plt.title('Top Workplaces with Consistently Low Fill Rates')
        plt.xlabel('Workplace ID')
        plt.ylabel('Fill Rate')
        plt.axhline(y=workplace_stats['fill_rate'].mean(), color='black', linestyle='--', 
                   label=f'Average Fill Rate: {workplace_stats["fill_rate"].mean():.2%}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOT_DIR / 'problematic_workplaces.png', dpi=300)
        plt.close()
        
        # Save problematic workplace data
        problematic_workplaces.to_csv(TABLE_DIR / 'problematic_workplaces.csv', index=False)
    
    # Workplace stickiness analysis
    # First, sort all data by workplace and timestamp to establish chronology
    df_sorted = df.sort_values(['workplace_id', 'shift_created_at'])
    
    # For each workplace, analyze their posting behavior over time
    workplace_shifts = {}
    for workplace in workplace_stats['workplace_id']:
        workplace_data = df_sorted[df_sorted['workplace_id'] == workplace]
        workplace_shifts[workplace] = workplace_data
    
    # Determine if there's a "stickiness point" for workplaces
    # How many successful shifts must be filled before a workplace becomes a regular poster?
    def get_workplace_retention(min_filled_shifts):
        retained = []
        for workplace_id, workplace_data in workplace_shifts.items():
            # Count filled shifts
            filled = workplace_data[workplace_data['is_verified']].sort_values('shift_start_at')
            if len(filled) >= min_filled_shifts:
                # Get date of the min_filled_shifts-th filled shift
                threshold_date = filled.iloc[min_filled_shifts-1]['shift_start_at']
                
                # Is there posting activity at least 30 days after that date?
                last_post = workplace_data['shift_created_at'].max()
                retained.append(1 if (last_post - threshold_date).days >= 30 else 0)
        
        return np.mean(retained) if retained else 0
    
    # Check retention rates at different filled shift thresholds
    thresholds = [1, 3, 5, 10, 15]
    retention_rates = [get_workplace_retention(t) for t in thresholds]
    
    workplace_retention = pd.DataFrame({
        'filled_shifts_threshold': thresholds,
        'retention_rate': retention_rates
    })
    
    # Plot workplace retention by filled shifts
    plt.figure(figsize=(12, 8))
    plt.plot(workplace_retention['filled_shifts_threshold'], 
            workplace_retention['retention_rate'], 
            'o-', color=COLORS['primary'], linewidth=2, markersize=10)
    
    plt.title('Workplace Retention Rate by Number of Filled Shifts')
    plt.xlabel('Number of Successfully Filled Shifts')
    plt.ylabel('Retention Rate')
    plt.grid(True, alpha=0.3)
    plt.xticks(thresholds)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'workplace_stickiness.png', dpi=300)
    plt.close()
    
    # Workplace clustering based on posting patterns
    # Need sufficient active workplaces
    active_workplaces = workplace_stats[workplace_stats['shifts_posted'] >= 5].copy()
    
    if len(active_workplaces) >= 20:  # Need enough data for meaningful clusters
        # Select features for clustering
        features = ['avg_rate', 'fill_rate', 'claim_rate', 'view_per_shift', 'deletion_rate']
        
        # Replace NaNs with appropriate values
        for feature in features:
            if feature in active_workplaces.columns:
                active_workplaces[feature] = active_workplaces[feature].fillna(active_workplaces[feature].median())
        
        # Add calculated features if available
        if 'lead_time_days' in df.columns:
            # Calculate average lead time by workplace
            lead_times = df.groupby('workplace_id')['lead_time_days'].mean().reset_index()
            lead_times.columns = ['workplace_id', 'avg_lead_time']
            
            # Add to active_workplaces
            active_workplaces = active_workplaces.merge(lead_times, on='workplace_id', how='left')
            active_workplaces['avg_lead_time'] = active_workplaces['avg_lead_time'].fillna(active_workplaces['avg_lead_time'].median())
            
            # Add to features
            features.append('avg_lead_time')
        
        # Calculate rate variability
        if 'shift_id' in df.columns and 'rate' in df.columns:
            # For each workplace, calculate standard deviation of rates
            rate_variability = df.groupby(['workplace_id', 'shift_id'])['rate'].mean().reset_index()
            rate_variability = rate_variability.groupby('workplace_id')['rate'].std().reset_index()
            rate_variability.columns = ['workplace_id', 'rate_std']
            
            # Add to active_workplaces
            active_workplaces = active_workplaces.merge(rate_variability, on='workplace_id', how='left')
            active_workplaces['rate_std'] = active_workplaces['rate_std'].fillna(0)  # No variability if only one rate
            
            # Add to features
            features.append('rate_std')
        
        # Standardize features
        X = active_workplaces[features].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters
        silhouette_scores = []
        for n_clusters in range(2, min(7, len(active_workplaces) // 5 + 1)):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
        
        # Choose optimal number of clusters
        optimal_clusters = silhouette_scores.index(max(silhouette_scores)) + 2
        print(f"Optimal number of workplace clusters: {optimal_clusters}")
        
        # Perform K-means clustering with optimal clusters
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
        active_workplaces['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Analyze cluster characteristics
        cluster_profiles = active_workplaces.groupby('cluster').agg({
            'workplace_id': 'count',
            'avg_rate': 'mean',
            'fill_rate': 'mean',
            'claim_rate': 'mean',
            'view_per_shift': 'mean',
            'deletion_rate': 'mean',
            'shifts_posted': 'mean'
        }).reset_index()
        
        # Add lead time and rate variability if available
        if 'avg_lead_time' in active_workplaces.columns:
            lead_time_means = active_workplaces.groupby('cluster')['avg_lead_time'].mean()
            cluster_profiles['avg_lead_time'] = cluster_profiles['cluster'].map(lead_time_means)
        
        if 'rate_std' in active_workplaces.columns:
            rate_std_means = active_workplaces.groupby('cluster')['rate_std'].mean()
            cluster_profiles['rate_variability'] = cluster_profiles['cluster'].map(rate_std_means)
        
        # Name the clusters based on characteristics
        cluster_names = []
        for _, row in cluster_profiles.iterrows():
            if 'avg_lead_time' in cluster_profiles.columns and 'rate_variability' in cluster_profiles.columns:
                if row['avg_lead_time'] > cluster_profiles['avg_lead_time'].median() and row['rate_variability'] < cluster_profiles['rate_variability'].median():
                    name = "Early Posters, Consistent Rates"
                elif row['avg_lead_time'] < cluster_profiles['avg_lead_time'].median() and row['rate_variability'] > cluster_profiles['rate_variability'].median():
                    name = "Last-Minute Posters, Variable Rates"
                elif row['avg_lead_time'] > cluster_profiles['avg_lead_time'].median() and row['rate_variability'] > cluster_profiles['rate_variability'].median():
                    name = "Early Posters, Variable Rates"
                elif row['avg_lead_time'] < cluster_profiles['avg_lead_time'].median() and row['rate_variability'] < cluster_profiles['rate_variability'].median():
                    name = "Last-Minute Posters, Consistent Rates"
                else:
                    name = f"Cluster {row['cluster']}"
            elif row['avg_rate'] > cluster_profiles['avg_rate'].median() and row['fill_rate'] > cluster_profiles['fill_rate'].median():
                name = "High Pay, High Fill"
            elif row['avg_rate'] < cluster_profiles['avg_rate'].median() and row['fill_rate'] < cluster_profiles['fill_rate'].median():
                name = "Low Pay, Low Fill"
            elif row['avg_rate'] > cluster_profiles['avg_rate'].median() and row['fill_rate'] < cluster_profiles['fill_rate'].median():
                name = "High Pay, Low Fill" 
            elif row['avg_rate'] < cluster_profiles['avg_rate'].median() and row['fill_rate'] > cluster_profiles['fill_rate'].median():
                name = "Low Pay, High Fill"
            else:
                name = f"Cluster {row['cluster']}"
            cluster_names.append(name)
        
        cluster_profiles['segment_name'] = cluster_names
        
        # Save workplace segments
        cluster_profiles.to_csv(TABLE_DIR / 'workplace_behavior_segments.csv', index=False)
        
        # Visualize clusters using PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        plt.figure(figsize=(12, 10))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=active_workplaces['cluster'], cmap='viridis', alpha=0.7)
        
        # Add cluster centers
        centers_pca = pca.transform(scaler.transform(kmeans.cluster_centers_))
        plt.scatter(centers_pca[:, 0], centers_pca[:, 1], c='red', s=100, alpha=0.8, marker='X')
        
        # Add labels
        for i, name in enumerate(cluster_names):
            plt.annotate(name, centers_pca[i], fontsize=12, 
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3))
        
        plt.title('Workplace Behavior Segments')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.colorbar(scatter, label='Cluster')
        plt.tight_layout()
        plt.savefig(PLOT_DIR / 'workplace_segments.png', dpi=300)
        plt.close()
    
    # Workplace confusion matrix - retention prediction
    # Get workplace attributes
    workplace_features = workplace_stats[['workplace_id', 'fill_rate', 'claim_rate', 'avg_rate', 'avg_margin']]
    
    # Define retention (posted shifts in the last 30 days of data)
    df_sorted = df.sort_values('shift_created_at')
    last_date = df_sorted['shift_created_at'].max()
    retention_threshold = last_date - pd.Timedelta(days=30)
    
    latest_posts = df.groupby('workplace_id')['shift_created_at'].max()
    retained_workplaces = latest_posts[latest_posts >= retention_threshold].index
    workplace_features['retained'] = workplace_features['workplace_id'].isin(retained_workplaces)
    
    # Build confusion matrix
    if len(workplace_features) > 20:  # Need enough data
        # Create quartiles for features
        for feature in ['fill_rate', 'claim_rate', 'avg_rate']:
            if feature in workplace_features.columns:
                workplace_features[f'{feature}_quartile'] = pd.qcut(
                    workplace_features[feature],
                    q=4,
                    labels=['Q1', 'Q2', 'Q3', 'Q4']
                )
        
        # Plot retention by fill rate quartile
        retention_by_fill = workplace_features.groupby('fill_rate_quartile')['retained'].mean().reset_index()
        
        plt.figure(figsize=(10, 8))
        sns.barplot(x='fill_rate_quartile', y='retained', data=retention_by_fill, color=COLORS['primary'])
        
        plt.title('Workplace Retention by Fill Rate Quartile')
        plt.xlabel('Fill Rate Quartile')
        plt.ylabel('Retention Rate')
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(PLOT_DIR / 'workplace_retention_confusion.png', dpi=300)
        plt.close()
    
    # Analyze risk of reliance on top workplaces
    # Calculate what would happen if we lost top X% of workplaces
    resilience_thresholds = [1, 5, 10, 20, 30]
    resilience_metrics = []
    
    for threshold in resilience_thresholds:
        # Calculate number of workplaces in this bucket
        n_workplaces = int(workplace_count * threshold / 100)
        
        # Get workplaces in this bucket
        top_workplaces = workplace_stats.head(n_workplaces)
        
        # Calculate metrics
        shifts_lost = top_workplaces['shifts_posted'].sum()
        shifts_lost_pct = shifts_lost / total_shifts * 100
        
        resilience_metrics.append({
            'top_workplace_pct': threshold,
            'workplace_count': n_workplaces,
            'shifts_lost': shifts_lost,
            'shifts_lost_pct': shifts_lost_pct
        })
    
    resilience_df = pd.DataFrame(resilience_metrics)
    
    # Save resilience metrics
    resilience_df.to_csv(TABLE_DIR / 'workplace_concentration_risk.csv', index=False)
    
    # Plot resilience metrics
    plt.figure(figsize=(10, 8))
    plt.plot(resilience_df['top_workplace_pct'], resilience_df['shifts_lost_pct'], 
             'o-', color=COLORS['danger'], linewidth=2, markersize=8)
    
    plt.title('Marketplace Resilience: Impact of Losing Top Workplaces')
    plt.xlabel('% of Top Workplaces Lost')
    plt.ylabel('% of Shifts Lost')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'workplace_resilience_impact.png', dpi=300)
    plt.close()
    
    return workplace_stats


def repeat_booking_analysis(df):
    """Analyze how frequently workers return to the same workplace."""
    print("Analyzing repeat booking patterns...")
    
    # Filter to claimed shifts (regardless of completion)
    claimed_shifts = df[df['claimed']].copy()
    
    # Create a flag to identify return bookings
    if len(claimed_shifts) > 0:
        # Sort by worker, workplace, and claim time
        claimed_shifts = claimed_shifts.sort_values(['worker_id', 'workplace_id', 'claimed_at'])
        
        # For each worker-workplace pair, flag if this is a return booking
        claimed_shifts['worker_workplace_visit_num'] = claimed_shifts.groupby(['worker_id', 'workplace_id']).cumcount() + 1
        claimed_shifts['is_return_worker'] = claimed_shifts['worker_workplace_visit_num'] > 1
    else:
        claimed_shifts['worker_workplace_visit_num'] = 1
        claimed_shifts['is_return_worker'] = False
    
    # Filter to completed shifts for the main analysis
    completed_shifts = claimed_shifts[claimed_shifts['is_verified']].copy()
    
    # Count shifts by worker-workplace pair
    repeat_bookings = completed_shifts.groupby(['worker_id', 'workplace_id']).size().reset_index(name='shifts_completed')
    
    # Distribution of repeat bookings
    booking_distribution = repeat_bookings.groupby('shifts_completed').size().reset_index(name='count')
    booking_distribution['percentage'] = booking_distribution['count'] / booking_distribution['count'].sum() * 100
    
    # Truncate to reasonable values for the chart
    max_repeats = 10  # Show up to 10 repeats, then group the rest
    
    if len(booking_distribution) > max_repeats:
        over_max = booking_distribution[booking_distribution['shifts_completed'] > max_repeats]
        truncated_distribution = booking_distribution[booking_distribution['shifts_completed'] <= max_repeats].copy()
        
        # Add the "More" category
        more_row = pd.DataFrame({
            'shifts_completed': [f'{max_repeats}+'],
            'count': [over_max['count'].sum()],
            'percentage': [over_max['percentage'].sum()]
        })
        
        truncated_distribution = pd.concat([truncated_distribution, more_row])
    else:
        truncated_distribution = booking_distribution
    
    # Plot distribution
    plt.figure(figsize=(12, 8))
    sns.barplot(x='shifts_completed', y='percentage', data=truncated_distribution, color=COLORS['primary'])
    
    plt.title('Distribution of Repeat Bookings')
    plt.xlabel('Number of Shifts Completed at Same Workplace')
    plt.ylabel('Percentage of Worker-Workplace Pairs')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'repeat_bookings_distribution.png', dpi=300)
    plt.close()
    
    # Save repeat booking distribution
    truncated_distribution.to_csv(TABLE_DIR / 'repeat_bookings_distribution.csv', index=False)
    
    # Analyze worker loyalty patterns
    # What percentage of a worker's shifts are at their most frequent workplace?
    worker_loyalty = completed_shifts.groupby(['worker_id', 'workplace_id']).size().reset_index(name='shifts')
    
    # Get total shifts by worker
    worker_totals = worker_loyalty.groupby('worker_id')['shifts'].sum().reset_index(name='total_shifts')
    
    # Find each worker's most frequent workplace
    worker_max = worker_loyalty.sort_values('shifts', ascending=False).drop_duplicates('worker_id')
    worker_max = worker_max.merge(worker_totals, on='worker_id')
    worker_max['loyalty_percent'] = worker_max['shifts'] / worker_max['total_shifts'] * 100
    
    # Calculate percentage of workers who do >50% of shifts at same workplace
    high_loyalty_workers = worker_max[worker_max['loyalty_percent'] > 50]
    pct_high_loyalty = len(high_loyalty_workers) / len(worker_max) if len(worker_max) > 0 else 0
    
    print(f"Workers who do >50% of shifts at the same workplace: {pct_high_loyalty:.2%}")
    
    # Plot loyalty distribution
    plt.figure(figsize=(12, 8))
    sns.histplot(worker_max['loyalty_percent'], bins=20, kde=True, color=COLORS['primary'])
    
    plt.title('Worker Loyalty - % of Shifts at Most Frequent Workplace')
    plt.xlabel('Percentage of Shifts')
    plt.ylabel('Number of Workers')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'worker_loyalty_distribution.png', dpi=300)
    plt.close()
    
    # Analyze the impact of workplace familiarity on no-show and cancellation rates
    # First, create a dataset of all claims with their shift count at each workplace
    completed_by_worker_workplace = df[df['claimed']].copy()
    
    # Add a "previous shifts at this workplace" counter
    worker_workplace_pairs = completed_by_worker_workplace[['worker_id', 'workplace_id', 'shift_id', 'claimed_at', 'is_ncns', 'canceled', 'is_verified']]
    worker_workplace_pairs = worker_workplace_pairs.sort_values(['worker_id', 'workplace_id', 'claimed_at'])
    
    # Group by worker and workplace
    worker_workplace_pairs['previous_shifts'] = worker_workplace_pairs.groupby(['worker_id', 'workplace_id']).cumcount()
    
    # Calculate cancellation and no-show rates by number of previous shifts
    familiarity_metrics = worker_workplace_pairs.groupby('previous_shifts').agg({
        'shift_id': 'count',
        'is_ncns': 'sum',
        'canceled': 'sum',
        'is_verified': 'sum'
    }).reset_index()
    
    familiarity_metrics['cancellation_rate'] = familiarity_metrics['canceled'] / familiarity_metrics['shift_id']
    familiarity_metrics['no_show_rate'] = familiarity_metrics['is_ncns'] / familiarity_metrics['shift_id']
    familiarity_metrics['completion_rate'] = familiarity_metrics['is_verified'] / familiarity_metrics['shift_id']
    
    # Limit to reasonable values for the chart
    familiarity_metrics = familiarity_metrics[familiarity_metrics['previous_shifts'] < 10]
    
    # Plot no-show rate by workplace familiarity
    plt.figure(figsize=(12, 8))
    sns.lineplot(x='previous_shifts', y='no_show_rate', data=familiarity_metrics, 
                marker='o', color=COLORS['danger'], linewidth=2, markersize=10)
    
    plt.title('No-Show Rate by Workplace Familiarity')
    plt.xlabel('Number of Previous Shifts at This Workplace')
    plt.ylabel('No-Show Rate')
    plt.xticks(familiarity_metrics['previous_shifts'])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'noshow_by_familiarity.png', dpi=300)
    plt.close()
    
    # Plot cancellation rate by workplace familiarity
    plt.figure(figsize=(12, 8))
    sns.lineplot(x='previous_shifts', y='cancellation_rate', data=familiarity_metrics, 
                marker='o', color=COLORS['warning'], linewidth=2, markersize=10)
    
    plt.title('Cancellation Rate by Workplace Familiarity')
    plt.xlabel('Number of Previous Shifts at This Workplace')
    plt.ylabel('Cancellation Rate')
    plt.xticks(familiarity_metrics['previous_shifts'])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'cancellation_by_familiarity.png', dpi=300)
    plt.close()
    
    # Save familiarity metrics
    familiarity_metrics.to_csv(TABLE_DIR / 'familiarity_impact.csv', index=False)
    
    # Analyze if some workplaces contribute to worker churn
    # Define a worker as "churned" if they haven't viewed shifts in the last 30 days
    last_date = df['offer_viewed_at'].max()
    churn_threshold = last_date - pd.Timedelta(days=30)
    
    # Get last view date for each worker
    last_view_date = df.groupby('worker_id')['offer_viewed_at'].max()
    churned_workers = last_view_date[last_view_date < churn_threshold].index
    
    # Get the last completed shift for each worker before they churned
    last_shifts = completed_shifts[completed_shifts['worker_id'].isin(churned_workers)].copy()
    if len(last_shifts) > 0:
        last_shifts = last_shifts.sort_values(['worker_id', 'shift_start_at'])
        last_shift_by_worker = last_shifts.groupby('worker_id').last().reset_index()
        
        # Count workers who churned after working at each workplace
        workplace_churn = last_shift_by_worker.groupby('workplace_id').size().reset_index(name='churned_workers')
        
        # Count total workers who ever worked at each workplace
        workplace_worker_counts = completed_shifts.groupby('workplace_id')['worker_id'].nunique().reset_index(name='total_workers')
        
        # Calculate churn rate by workplace
        workplace_churn = workplace_churn.merge(workplace_worker_counts, on='workplace_id', how='left')
        workplace_churn['churn_rate'] = workplace_churn['churned_workers'] / workplace_churn['total_workers']
        
        # Filter to workplaces with sufficient sample size
        workplace_churn = workplace_churn[workplace_churn['total_workers'] >= 5]
        
        # Sort by churn rate
        workplace_churn = workplace_churn.sort_values('churn_rate', ascending=False)
        
        # Identify high-churn workplaces (top 20%)
        if len(workplace_churn) > 0:
            churn_threshold = workplace_churn['churn_rate'].quantile(0.8)
            high_churn_workplaces = workplace_churn[workplace_churn['churn_rate'] >= churn_threshold]
            
            print(f"Found {len(high_churn_workplaces)} workplaces with abnormally high worker churn rates (>{churn_threshold:.2%})")
            
            # Calculate average churn rate
            avg_churn_rate = workplace_churn['churn_rate'].mean()
            print(f"Average workplace churn rate: {avg_churn_rate:.2%}")
            
            # Save workplace churn metrics
            workplace_churn.to_csv(TABLE_DIR / 'workplace_churn_rates.csv', index=False)
            
            # Plot top 10 highest churn workplaces
            top_n = min(10, len(workplace_churn))
            plt.figure(figsize=(12, 8))
            sns.barplot(x='churn_rate', y='workplace_id', data=workplace_churn.head(top_n), color=COLORS['danger'])
            
            plt.title('Workplaces with Highest Worker Churn Rates')
            plt.xlabel('Churn Rate')
            plt.ylabel('Workplace ID')
            plt.axvline(x=avg_churn_rate, color='black', linestyle='--', label=f'Average ({avg_churn_rate:.2%})')
            plt.legend()
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'workplace_negative_experience.png', dpi=300)
            plt.close()
    
    # Add critical metrics to familiarity_metrics for use in detailed_analysis
    if len(claimed_shifts) > 0:
        # Calculate percentage of workers returning to the same workplace
        returning_workers_pct = claimed_shifts['is_return_worker'].mean()
        
        # Calculate cancellation rates by familiarity
        familiar_cancel_rate = claimed_shifts[claimed_shifts['is_return_worker']]['canceled'].mean() if len(claimed_shifts[claimed_shifts['is_return_worker']]) > 0 else 0
        new_cancel_rate = claimed_shifts[~claimed_shifts['is_return_worker']]['canceled'].mean() if len(claimed_shifts[~claimed_shifts['is_return_worker']]) > 0 else 0
        
        # Calculate pay premium for unfamiliar workplaces
        avg_rate_familiar = claimed_shifts[claimed_shifts['is_return_worker']]['rate'].mean() if len(claimed_shifts[claimed_shifts['is_return_worker']]) > 0 else 0
        avg_rate_unfamiliar = claimed_shifts[~claimed_shifts['is_return_worker']]['rate'].mean() if len(claimed_shifts[~claimed_shifts['is_return_worker']]) > 0 else 0
        unfamiliar_pay_premium = avg_rate_unfamiliar - avg_rate_familiar if avg_rate_familiar > 0 else 0
        
        # Add these metrics as DataFrame attributes
        familiarity_metrics.attrs['returning_workers_pct'] = returning_workers_pct
        familiarity_metrics.attrs['familiar_cancel_rate'] = familiar_cancel_rate 
        familiarity_metrics.attrs['new_cancel_rate'] = new_cancel_rate
        familiarity_metrics.attrs['unfamiliar_pay_premium'] = unfamiliar_pay_premium
    
    # Return everything in a dictionary for easier access
    return {
        'booking_distribution': truncated_distribution,
        'worker_loyalty': worker_max,
        'familiarity_metrics': familiarity_metrics,
        'claimed_shifts': claimed_shifts
    }


def shift_deletion_analysis(df):
    """Analyze patterns in shift deletions."""
    print("Analyzing shift deletion patterns...")
    
    # Filter to deleted shifts
    deleted_shifts = df[df['deleted']].copy()
    
    if len(deleted_shifts) == 0:
        print("No deleted shifts in the dataset")
        return None, None
    
    # Calculate overall deletion rate
    total_shifts = df['shift_id'].nunique()
    deleted_shift_ids = deleted_shifts['shift_id'].unique()
    deletion_rate = len(deleted_shift_ids) / total_shifts
    
    print(f"Overall shift deletion rate: {deletion_rate:.2%}")
    
    # Analyze timing of deletions
    if 'shift_created_at' in deleted_shifts.columns and 'deleted_at' in deleted_shifts.columns:
        # Calculate time between creation and deletion
        deleted_shifts['hours_to_deletion'] = (deleted_shifts['deleted_at'] - deleted_shifts['shift_created_at']).dt.total_seconds() / 3600
        
        # Create time buckets
        bins = [0, 1, 3, 6, 12, 24, 48, 72, 168, float('inf')]
        labels = ['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '1-2d', '2-3d', '3-7d', '>7d']
        deleted_shifts['deletion_time_bucket'] = pd.cut(deleted_shifts['hours_to_deletion'], bins=bins, labels=labels)
        
        # Count deletions by time bucket
        deletion_times = deleted_shifts['deletion_time_bucket'].value_counts().sort_index().reset_index()
        deletion_times.columns = ['time_after_creation', 'count']
        
        # Calculate percentage
        deletion_times['percentage'] = deletion_times['count'] / deletion_times['count'].sum() * 100
        
        # Plot deletion timing
        plt.figure(figsize=(12, 8))
        sns.barplot(x='time_after_creation', y='percentage', data=deletion_times, color=COLORS['primary'])
        
        plt.title('When Are Shifts Deleted After Creation?')
        plt.xlabel('Time After Shift Creation')
        plt.ylabel('Percentage of Deletions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(PLOT_DIR / 'deletion_timing.png', dpi=300)
        plt.close()
        
        # Save deletion timing data
        deletion_times.to_csv(TABLE_DIR / 'deletion_timing.csv', index=False)
    
    # Analyze deletions relative to shift start time
    if 'shift_start_at' in deleted_shifts.columns and 'deleted_at' in deleted_shifts.columns:
        # Calculate time between deletion and shift start
        deleted_shifts['hours_before_start'] = (deleted_shifts['shift_start_at'] - deleted_shifts['deleted_at']).dt.total_seconds() / 3600
        
        # Filter to deletions before shift start
        pre_start_deletions = deleted_shifts[deleted_shifts['hours_before_start'] > 0].copy()
        
        if len(pre_start_deletions) > 0:
            # Create time buckets
            bins = [0, 1, 3, 6, 12, 24, 48, 72, 168, float('inf')]
            labels = ['<1h', '1-3h', '3-6h', '6-12h', '12-24h', '1-2d', '2-3d', '3-7d', '>7d']
            pre_start_deletions['time_before_start_bucket'] = pd.cut(pre_start_deletions['hours_before_start'], bins=bins, labels=labels)
            
            # Count deletions by time bucket
            deletion_start_times = pre_start_deletions['time_before_start_bucket'].value_counts().sort_index().reset_index()
            deletion_start_times.columns = ['time_before_shift_start', 'count']
            
            # Calculate percentage
            deletion_start_times['percentage'] = deletion_start_times['count'] / deletion_start_times['count'].sum() * 100
            
            # Plot deletion timing relative to shift start
            plt.figure(figsize=(12, 8))
            sns.barplot(x='time_before_shift_start', y='percentage', data=deletion_start_times, color=COLORS['secondary'])
            
            plt.title('When Are Shifts Deleted Before Start Time?')
            plt.xlabel('Time Before Shift Start')
            plt.ylabel('Percentage of Deletions')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'deletion_before_start.png', dpi=300)
            plt.close()
            
            # Save deletion timing data
            deletion_start_times.to_csv(TABLE_DIR / 'deletion_before_start.csv', index=False)
    
    # Analyze workplace-specific deletion patterns
    if 'workplace_id' in deleted_shifts.columns:
        # Calculate deletion count by workplace
        workplace_deletions = deleted_shifts.groupby('workplace_id')['shift_id'].nunique().reset_index()
        workplace_deletions.columns = ['workplace_id', 'deleted_shifts']
        
        # Get total shifts posted by each workplace
        total_by_workplace = df.groupby('workplace_id')['shift_id'].nunique().reset_index()
        total_by_workplace.columns = ['workplace_id', 'total_shifts']
        
        # Merge data
        workplace_deletions = workplace_deletions.merge(total_by_workplace, on='workplace_id')
        
        # Calculate deletion rate
        workplace_deletions['deletion_rate'] = workplace_deletions['deleted_shifts'] / workplace_deletions['total_shifts']
        
        # Filter to workplaces with sufficient volume
        workplace_deletions = workplace_deletions[workplace_deletions['total_shifts'] >= 10]
        
        if len(workplace_deletions) > 0:
            # Calculate average deletion rate
            avg_deletion_rate = workplace_deletions['deletion_rate'].mean()
            
            # Identify high deletion workplaces (top 20%)
            deletion_threshold = workplace_deletions['deletion_rate'].quantile(0.8)
            high_deletion_workplaces = workplace_deletions[workplace_deletions['deletion_rate'] >= deletion_threshold]
            
            print(f"Average workplace deletion rate: {avg_deletion_rate:.2%}")
            print(f"Found {len(high_deletion_workplaces)} workplaces with abnormally high deletion rates (>{deletion_threshold:.2%})")
            
            # Plot top 10 highest deletion workplaces
            top_n = min(10, len(workplace_deletions))
            plt.figure(figsize=(12, 8))
            sns.barplot(x='deletion_rate', y='workplace_id', data=workplace_deletions.head(top_n), color=COLORS['warning'])
            
            plt.title('Workplaces with Highest Shift Deletion Rates')
            plt.xlabel('Deletion Rate')
            plt.ylabel('Workplace ID')
            plt.axvline(x=avg_deletion_rate, color='black', linestyle='--', label=f'Average ({avg_deletion_rate:.2%})')
            plt.legend()
            plt.tight_layout()
            plt.savefig(PLOT_DIR / 'high_deletion_workplaces.png', dpi=300)
            plt.close()
            
            # Save workplace deletion metrics
            workplace_deletions.to_csv(TABLE_DIR / 'workplace_deletion_patterns.csv', index=False)
            
            # Analyze worker engagement after experiencing a deletion
            # Get all workers who experienced at least one deleted shift
            workers_with_deletions = deleted_shifts['worker_id'].unique()
            
            # For each worker, calculate engagement before and after their first deletion experience
            if len(workers_with_deletions) > 0:
                worker_deletion_impact = []
                
                for worker_id in workers_with_deletions:
                    worker_data = df[df['worker_id'] == worker_id].sort_values('offer_viewed_at')
                    worker_deletions = deleted_shifts[deleted_shifts['worker_id'] == worker_id].sort_values('deleted_at')
                    
                    if len(worker_deletions) > 0:
                        first_deletion = worker_deletions.iloc[0]['deleted_at']
                        
                        before_deletion = worker_data[worker_data['offer_viewed_at'] < first_deletion]
                        after_deletion = worker_data[worker_data['offer_viewed_at'] >= first_deletion]
                        
                        # Need sufficient data before and after
                        if len(before_deletion) >= 3 and len(after_deletion) >= 3:
                            worker_deletion_impact.append({
                                'worker_id': worker_id,
                                'claim_rate_before': before_deletion['claimed'].mean(),
                                'claim_rate_after': after_deletion['claimed'].mean(),
                                'views_before': len(before_deletion),
                                'views_after': len(after_deletion)
                            })
                
                if len(worker_deletion_impact) > 0:
                    deletion_impact_df = pd.DataFrame(worker_deletion_impact)
                    deletion_impact_df['claim_rate_change'] = deletion_impact_df['claim_rate_after'] - deletion_impact_df['claim_rate_before']
                    
                    # Calculate average impact
                    avg_claim_change = deletion_impact_df['claim_rate_change'].mean()
                    pct_decreased = (deletion_impact_df['claim_rate_change'] < 0).mean() * 100
                    
                    print(f"Impact of experiencing a shift deletion on worker claim rate: {avg_claim_change:.2%}")
                    print(f"Percentage of workers with decreased claim rate after deletion: {pct_decreased:.1f}%")
                    
                    # Save deletion impact data
                    deletion_impact_df.to_csv(TABLE_DIR / 'deletion_impact_on_workers.csv', index=False)
    
    return deletion_times if 'deletion_times' in locals() else None, workplace_deletions if 'workplace_deletions' in locals() else None