import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_performance_trends(df):
    """Create performance trends visualization"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Performance Scores', 'Weekly Patterns')
    )
    
    # Daily performance trend
    daily_avg = df.groupby(df['timestamp'].dt.date).agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean',
        'mood_score': 'mean'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=daily_avg['timestamp'],
            y=daily_avg['focus_score'],
            name='Focus Score',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Weekly patterns
    weekly = df.groupby(df['timestamp'].dt.dayofweek).agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean',
        'mood_score': 'mean'
    }).reset_index()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly['day'] = weekly['timestamp'].map(lambda x: days[x])
    
    fig.add_trace(
        go.Bar(
            x=weekly['day'],
            y=weekly['focus_score'],
            name='Average Focus Score'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=800,
        title_text="Performance Trends",
        showlegend=True
    )
    
    return fig

def create_lifestyle_impact_chart(df):
    """Create visualization showing impact of lifestyle factors"""
    # Sleep impact
    sleep_impact = df.groupby('sleep_quality').agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean'
    }).reset_index()
    
    # Exercise impact
    exercise_impact = df.groupby('exercise_type').agg({
        'focus_score': 'mean',
        'mental_clarity': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Sleep Quality Impact', 'Exercise Type Impact')
    )
    
    fig.add_trace(
        go.Bar(
            x=sleep_impact['sleep_quality'],
            y=sleep_impact['focus_score'],
            name='Focus Score'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=exercise_impact['exercise_type'],
            y=exercise_impact['focus_score'],
            name='Focus Score'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="Lifestyle Factors Impact",
        showlegend=True
    )
    
    return fig