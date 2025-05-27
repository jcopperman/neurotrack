import plotly.express as px
import plotly.graph_objects as go

def create_activity_metrics_chart(activity_metrics):
    """Create bar chart showing metrics by activity type"""
    fig = px.bar(
        activity_metrics.melt(id_vars=['activity_type']),
        x='activity_type',
        y='value',
        color='variable',
        title='Cognitive Metrics by Activity Type',
        labels={
            'activity_type': 'Activity Type',
            'value': 'Score',
            'variable': 'Metric'
        },
        barmode='group'
    )
    return fig

def create_optimal_activities_chart(time_activity_metrics):
    """Create scatter plot showing activity performance by time of day"""
    fig = px.scatter(
        time_activity_metrics,
        x='hour',
        y='performance',
        color='activity_type',
        title='Activity Performance by Time of Day',
        labels={
            'hour': 'Hour of Day',
            'performance': 'Performance Score',
            'activity_type': 'Activity Type'
        },
        size='performance'
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            ticktext=[f"{i:02d}:00" for i in range(24)],
            tickvals=list(range(24))
        ),
        yaxis=dict(
            title="Performance Score (0-5)"
        )
    )
    return fig

def get_activity_recommendations(time_activity_metrics):
    """Generate activity recommendations for different times of day based on performance"""
    # Find best activity for each time period
    morning = time_activity_metrics[time_activity_metrics['hour'].between(6, 11)]
    afternoon = time_activity_metrics[time_activity_metrics['hour'].between(12, 17)]
    evening = time_activity_metrics[time_activity_metrics['hour'].between(18, 23)]
    
    # Get the activity with highest average performance for each period
    morning_best = morning.groupby('activity_type')['performance'].mean().nlargest(1).index[0]
    afternoon_best = afternoon.groupby('activity_type')['performance'].mean().nlargest(1).index[0]
    evening_best = evening.groupby('activity_type')['performance'].mean().nlargest(1).index[0]
    
    return {
        'morning': morning_best,
        'afternoon': afternoon_best,
        'evening': evening_best
    }