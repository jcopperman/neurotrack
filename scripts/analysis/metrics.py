import pandas as pd
import numpy as np

def calculate_hourly_stats(df):
    """Calculate hourly performance statistics from session data"""
    # Add time analysis
    df['hour'] = pd.to_datetime(df['time_of_day'], format='%H:%M').dt.hour.astype(int)
    
    # Calculate hourly statistics
    hourly_stats = df.groupby('hour').agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean',
        'mood_score': 'mean'
    }).reset_index()
    
    hourly_stats['hour'] = hourly_stats['hour'].astype(int)
    return hourly_stats

def normalize_metrics(df, columns, scale=(0, 5)):
    """Normalize metrics to a given scale"""
    min_val, max_val = scale
    for col in columns:
        if col in df.columns:
            norm_col = f'{col}_norm'
            df[norm_col] = (
                (df[col] - df[col].min()) /
                (df[col].max() - df[col].min()) * (max_val - min_val) + min_val
            )
    return df

def calculate_performance_score(df, weights=None):
    """Calculate overall performance score based on multiple metrics"""
    if weights is None:
        weights = {
            'focus_score': 0.25,
            'mental_clarity': 0.25,
            'mood_score': 0.2,
            'focus_indicator_norm': 0.15,
            'engagement_norm': 0.15
        }
    
    score = 0
    for metric, weight in weights.items():
        if metric in df.columns:
            score += df[metric] * weight
    
    return score

def find_optimal_times(hourly_stats, n=3):
    """Find the n best performing hours"""
    return hourly_stats.nlargest(n, 'performance_score')

def analyze_activity_patterns(df):
    """Analyze performance patterns by activity type"""
    activity_metrics = df.groupby('activity_type').agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean',
        'mood_score': 'mean'
    }).reset_index()
    
    # Calculate overall performance for each activity
    activity_metrics['performance'] = calculate_performance_score(activity_metrics)
    
    return activity_metrics