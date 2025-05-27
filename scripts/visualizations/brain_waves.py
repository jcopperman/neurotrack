import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_band_powers_chart(band_powers):
    """Create a radar chart showing relative band powers"""
    if not band_powers:
        return None
        
    bands = list(band_powers.keys())
    values = list(band_powers.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=bands,
        fill='toself'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)]
            )),
        showlegend=False,
        title='Brain Wave Band Powers'
    )
    
    return fig

def create_cognitive_metrics_chart(hourly_stats):
    """Create time series chart of cognitive metrics"""
    fig = go.Figure()
    
    if 'focus_indicator_norm' in hourly_stats.columns:
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'], 
            y=hourly_stats['focus_indicator_norm'],
            name='EEG Focus',
            line=dict(color='blue')
        ))
    
    if 'engagement_norm' in hourly_stats.columns:
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'], 
            y=hourly_stats['engagement_norm'],
            name='EEG Engagement',
            line=dict(color='green')
        ))
    
    fig.add_trace(go.Scatter(
        x=hourly_stats['hour'], 
        y=hourly_stats['focus_score'],
        name='Self-Reported Focus',
        line=dict(dash='dash', color='gray')
    ))
    
    fig.update_layout(
        title='Cognitive Metrics Over Time',
        xaxis_title='Hour of Day',
        yaxis_title='Score (Normalized)',
        hovermode='x unified'
    )
    
    return fig