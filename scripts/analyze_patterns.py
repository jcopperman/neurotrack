import sqlite3
import pandas as pd
import numpy as np
from scipy.signal import welch
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json

class CognitivePatternAnalyzer:
    def __init__(self, db_path='data/neurotrack.db'):
        self.db_path = db_path

    def load_data(self, user_id=None):
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT 
            s.id,
            s.user_id,
            u.name as user_name,
            s.timestamp,
            s.eeg_file_path,
            lc.*
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        JOIN lifestyle_context lc ON s.id = lc.session_id
        '''
        if user_id:
            query += f' WHERE s.user_id = {user_id}'
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Convert time_of_day to datetime for easier analysis
        df['hour'] = pd.to_datetime(df['time_of_day'], format='%H:%M').dt.hour
        return df

    def analyze_optimal_times(self, df):
        """Analyze cognitive performance by time of day"""
        # Calculate average performance metrics by hour
        hourly_metrics = df.groupby('hour').agg({
            'focus_score': 'mean',
            'mental_clarity': 'mean',
            'mood_score': 'mean'
        }).reset_index()
        
        # Calculate composite performance score
        hourly_metrics['performance_score'] = (
            hourly_metrics['focus_score'] * 0.4 +
            hourly_metrics['mental_clarity'] * 0.4 +
            hourly_metrics['mood_score'] * 0.2
        )
        
        return hourly_metrics

    def analyze_activity_patterns(self, df):
        """Analyze performance patterns by activity type"""
        activity_metrics = df.groupby(['activity_type', 'hour']).agg({
            'focus_score': 'mean',
            'mental_clarity': 'mean'
        }).reset_index()
        
        return activity_metrics

    def analyze_eeg_patterns(self, eeg_file):
        """Analyze EEG frequency bands to assess cognitive state"""
        try:
            eeg_data = pd.read_csv(eeg_file)
            
            # Calculate power spectral density
            fs = 256  # sampling frequency
            f, pxx = welch(eeg_data['channel1'], fs=fs)
            
            # Extract frequency bands
            delta = np.mean(pxx[(f >= 0.5) & (f <= 4)])    # 0.5-4 Hz
            theta = np.mean(pxx[(f >= 4) & (f <= 8)])      # 4-8 Hz
            alpha = np.mean(pxx[(f >= 8) & (f <= 13)])     # 8-13 Hz
            beta = np.mean(pxx[(f >= 13) & (f <= 30)])     # 13-30 Hz
            
            # Calculate focus indicators
            focus_ratio = beta / (theta + alpha)  # Higher ratio indicates better focus
            
            return {
                'focus_ratio': focus_ratio,
                'alpha_power': alpha,
                'beta_power': beta
            }
        except:
            return None

    def generate_insights(self, user_id=None):
        """Generate comprehensive insights about optimal work patterns"""
        df = self.load_data(user_id)
        
        # Analyze optimal times
        hourly_metrics = self.analyze_optimal_times(df)
        peak_hours = hourly_metrics.nlargest(3, 'performance_score')
        
        # Analyze activity patterns
        activity_patterns = self.analyze_activity_patterns(df)
        
        # Generate insights
        insights = {
            'peak_performance_hours': peak_hours['hour'].tolist(),
            'optimal_deep_work_time': self._get_optimal_activity_time(df, 'deep_work'),
            'optimal_creative_time': self._get_optimal_activity_time(df, 'creative'),
            'best_conditions': self._analyze_best_conditions(df)
        }
        
        return insights, hourly_metrics, activity_patterns

    def _get_optimal_activity_time(self, df, activity):
        activity_df = df[df['activity_type'] == activity]
        if len(activity_df) == 0:
            return None
            
        performance = (activity_df['focus_score'] + activity_df['mental_clarity']) / 2
        best_sessions = activity_df.loc[performance.nlargest(3).index]
        
        return {
            'hours': best_sessions['hour'].tolist(),
            'avg_focus': best_sessions['focus_score'].mean(),
            'avg_clarity': best_sessions['mental_clarity'].mean()
        }

    def _analyze_best_conditions(self, df):
        best_sessions = df.nlargest(10, ['focus_score', 'mental_clarity']).agg({
            'sleep_hours': 'mean',
            'hours_since_meal': 'mean',
            'exercise_type': lambda x: x.mode().iloc[0],
            'last_meal_type': lambda x: x.mode().iloc[0]
        })
        
        return best_sessions.to_dict()

if __name__ == "__main__":
    analyzer = CognitivePatternAnalyzer()
    
    # Generate insights for all users
    conn = sqlite3.connect('data/neurotrack.db')
    users = pd.read_sql_query('SELECT id, name FROM users', conn)
    conn.close()
    
    for _, user in users.iterrows():
        insights, hourly_metrics, activity_patterns = analyzer.generate_insights(user['id'])
        
        # Save insights to JSON
        with open(f'data/analysis/insights_user_{user["id"]}.json', 'w') as f:
            json.dump(insights, f, indent=4)
        
        # Generate visualizations
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Daily Performance Pattern", "Activity-Specific Performance")
        )
        
        # Daily pattern plot
        fig.add_trace(
            go.Scatter(x=hourly_metrics['hour'], 
                      y=hourly_metrics['performance_score'],
                      name="Overall Performance"),
            row=1, col=1
        )
        
        # Activity pattern plot
        for activity in activity_patterns['activity_type'].unique():
            activity_data = activity_patterns[activity_patterns['activity_type'] == activity]
            fig.add_trace(
                go.Scatter(x=activity_data['hour'],
                          y=activity_data['focus_score'],
                          name=f"{activity} Focus"),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            title_text=f"Cognitive Performance Analysis - {user['name']}"
        )
        fig.write_html(f'data/analysis/performance_patterns_user_{user["id"]}.html')
        
    print("Analysis complete! Check data/analysis/ directory for results.")
