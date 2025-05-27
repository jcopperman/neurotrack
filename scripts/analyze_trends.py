import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class NeuroAnalyzer:
    def __init__(self):
        self.db_path = 'data/neurotrack.db'
        self.output_dir = Path('data/analysis')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_sessions_data(self):
        """Load all sessions with their context data"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT 
            s.id as session_id,
            s.timestamp,
            lc.sleep_hours,
            lc.sleep_quality,
            lc.last_meal_type,
            lc.hours_since_meal,
            lc.exercise_type,
            lc.exercise_duration_mins,
            lc.mood_score
        FROM sessions s
        JOIN lifestyle_context lc ON s.id = lc.session_id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def analyze_sleep_impact(self, df):
        """Analyze the relationship between sleep and mood/performance"""
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='sleep_hours', y='mood_score', size='sleep_quality', 
                       sizes=(50, 200), alpha=0.6)
        plt.title('Sleep Duration vs Mood Score')
        plt.xlabel('Sleep Hours')
        plt.ylabel('Mood Score')
        plt.savefig(self.output_dir / 'sleep_analysis.png')
        plt.close()

    def analyze_meal_timing(self, df):
        """Analyze the impact of meal timing on mood/performance"""
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='last_meal_type', y='mood_score')
        plt.title('Meal Type vs Mood Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'meal_analysis.png')
        plt.close()

    def generate_report(self):
        """Generate a complete analysis report"""
        df = self.load_sessions_data()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Generate visualizations
        self.analyze_sleep_impact(df)
        self.analyze_meal_timing(df)
        
        # Calculate summary statistics
        summary = {
            'total_sessions': len(df),
            'avg_sleep_hours': df['sleep_hours'].mean(),
            'avg_mood_score': df['mood_score'].mean(),
            'best_meal_type': df.groupby('last_meal_type')['mood_score'].mean().idxmax()
        }
        
        # Save summary to file
        with open(self.output_dir / 'summary.txt', 'w') as f:
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        
        return summary

if __name__ == "__main__":
    analyzer = NeuroAnalyzer()
    summary = analyzer.generate_report()
    print("Analysis complete! Check the data/analysis directory for results.")
