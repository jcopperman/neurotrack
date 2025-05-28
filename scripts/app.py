import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import plotly.graph_objects as go

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from scripts.analysis.eeg import analyze_eeg_data
from scripts.log_session import SessionLogger

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = 1  # Default to user 1 for now

# Initialize database connection
def get_db_connection():
    return sqlite3.connect('data/neurotrack.db', timeout=20)  # Add timeout to handle locks

# Set page config
st.set_page_config(
    page_title="Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Sidebar
st.sidebar.title("🧠 NeuroTrack")
st.sidebar.markdown("---")

# User filter
with get_db_connection() as conn:
    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)

# Get the current user's name from the session state
current_user_name = users_df[users_df['id'] == st.session_state.current_user]['name'].iloc[0]

# Get the index of the current user
current_user_index = int(users_df[users_df['id'] == st.session_state.current_user].index[0])

selected_user = st.sidebar.selectbox(
    "Select User",
    users_df['name'].tolist(),
    index=current_user_index
)

# Update session state when user changes
if selected_user != current_user_name:
    st.session_state.current_user = users_df[users_df['name'] == selected_user]['id'].iloc[0]

# Get user ID from session state
user_id = st.session_state.current_user

# Date range filter
with get_db_connection() as conn:
    # First get unique timestamps
    sessions_df = pd.read_sql_query(
        """
        SELECT DISTINCT timestamp 
        FROM sessions 
        WHERE user_id = ? 
        ORDER BY timestamp
        """,
        conn,
        params=(user_id,)
    )

if not sessions_df.empty:
    try:
        # Convert timestamp to datetime safely
        timestamps = []
        for ts in sessions_df['timestamp']:
            try:
                # Try parsing as string with microseconds first
                timestamps.append(pd.to_datetime(ts, format='%Y-%m-%d %H:%M:%S.%f'))
            except:
                try:
                    # If that fails, try parsing as Unix timestamp
                    timestamps.append(pd.to_datetime(ts, unit='s'))
                except:
                    # If both fail, try default parsing
                    timestamps.append(pd.to_datetime(ts))
        
        if timestamps:
            sessions_df['timestamp'] = timestamps
            min_date = min(timestamps).date()
            max_date = max(timestamps).date()
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = (datetime.now().date(), datetime.now().date())
            st.sidebar.warning("No valid timestamps found for this user")
    except Exception as e:
        st.error(f"Error processing dates: {str(e)}")
        date_range = (datetime.now().date(), datetime.now().date())
else:
    date_range = (datetime.now().date(), datetime.now().date())
    st.sidebar.warning("No sessions found for this user")

# Main content
st.title(f"Dashboard - {selected_user}")

# Create tabs for different views
tabs = st.tabs([
    "📊 Performance Overview", 
    "📝 Journal Entry",
    "🍽️ Diet Log",
    "📈 Analysis",
    "💡 Recommendations"
])

# Performance Overview Tab
with tabs[0]:
    st.header("📊 Performance Overview")
    
    # Load recent sessions
    with get_db_connection() as conn:
        try:
            sessions_df = pd.read_sql_query("""
                SELECT DISTINCT 
                    s.id, 
                    s.timestamp, 
                    s.user_id,
                    lc.sleep_quality,
                    lc.mood_score,
                    lc.focus_score,
                    lc.mental_clarity,
                    je.energy_level,
                    je.productivity_score
                FROM sessions s
                LEFT JOIN lifestyle_context lc ON s.id = lc.session_id
                LEFT JOIN journal_entries je ON s.id = je.session_id
                WHERE s.user_id = ?
                ORDER BY s.timestamp DESC
                LIMIT 10
            """, conn, params=(user_id,))
            
            # Convert timestamp to datetime safely
            if not sessions_df.empty:
                timestamps = []
                for ts in sessions_df['timestamp']:
                    try:
                        # Try parsing as string with microseconds first
                        timestamps.append(pd.to_datetime(ts, format='%Y-%m-%d %H:%M:%S.%f'))
                    except:
                        try:
                            # If that fails, try parsing as Unix timestamp
                            timestamps.append(pd.to_datetime(ts, unit='s'))
                        except:
                            # If both fail, try default parsing
                            timestamps.append(pd.to_datetime(ts))
                
                if timestamps:
                    sessions_df['timestamp'] = timestamps
        except Exception as e:
            st.error(f"Error loading sessions: {str(e)}")
            sessions_df = pd.DataFrame()
    
    if not sessions_df.empty:
        # Display recent sessions
        st.subheader("Recent Sessions")
        for _, session in sessions_df.iterrows():
            with st.expander(f"Session {session['id']} - {session['timestamp']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if pd.notna(session['sleep_quality']):
                        st.metric("Sleep Quality", f"{session['sleep_quality']}/5")
                    if pd.notna(session['mood_score']):
                        st.metric("Mood Score", f"{session['mood_score']}/5")
                
                with col2:
                    if pd.notna(session['focus_score']):
                        st.metric("Focus Score", f"{session['focus_score']}/5")
                    if pd.notna(session['mental_clarity']):
                        st.metric("Mental Clarity", f"{session['mental_clarity']}/5")
                
                with col3:
                    if pd.notna(session['energy_level']):
                        st.metric("Energy Level", f"{session['energy_level']}/5")
                    if pd.notna(session['productivity_score']):
                        st.metric("Productivity", f"{session['productivity_score']}/5")
                
                # Show EEG analysis if available
                eeg_analysis = analyze_eeg_data(session['id'])
                if eeg_analysis:
                    st.subheader("EEG Analysis")
                    metrics = eeg_analysis['cognitive_metrics']
                    st.write(f"Focus Score: {metrics['focus_score']}/5")
                    st.write(f"Relaxation Score: {metrics['relaxation_score']}/5")
                    st.write(f"Mental Clarity: {metrics['clarity_score']}/5")

# Journal Entry Tab
with tabs[1]:
    st.header("📝 Journal Entry")
    
    with st.form("journal_entry_form"):
        # Mood and Energy
        col1, col2 = st.columns(2)
        with col1:
            mood = st.text_input("Current Mood", placeholder="e.g., focused, relaxed, anxious")
            energy_level = st.slider("Energy Level", 1, 5, 3)
        with col2:
            stress_level = st.slider("Stress Level", 1, 5, 3)
            productivity_score = st.slider("Productivity Score", 1, 5, 3)
        
        # Notes and Tags
        notes = st.text_area("Notes", placeholder="How are you feeling? What's on your mind?")
        tags = st.text_input("Tags (comma-separated)", placeholder="e.g., work, focus, creative")
        
        # Submit button
        submitted = st.form_submit_button("Save Journal Entry")
        
        if submitted:
            # Create journal entry
            journal_entry = {
                'mood': mood,
                'energy_level': energy_level,
                'stress_level': stress_level,
                'productivity_score': productivity_score,
                'notes': notes,
                'tags': tags
            }
            
            # Save journal entry
            logger = SessionLogger()
            if logger.log_session(
                user_id=user_id,
                journal_entry=journal_entry
            ):
                st.success("Journal entry saved successfully!")
            else:
                st.error("Error saving journal entry")

# Diet Log Tab
with tabs[2]:
    st.header("🍽️ Diet Log")
    
    with st.form("diet_log_form"):
        # Meal Information
        col1, col2 = st.columns(2)
        with col1:
            meal_type = st.selectbox(
                "Meal Type",
                ["breakfast", "lunch", "dinner", "snack"]
            )
            food_items = st.text_area(
                "Food Items",
                placeholder="Enter food items (one per line)"
            )
        
        with col2:
            calories = st.number_input("Calories", min_value=0, step=10)
            protein = st.number_input("Protein (g)", min_value=0.0, step=0.1)
            carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1)
            fats = st.number_input("Fats (g)", min_value=0.0, step=0.1)
        
        # Additional Nutrition
        col3, col4 = st.columns(2)
        with col3:
            fiber = st.number_input("Fiber (g)", min_value=0.0, step=0.1)
            sugar = st.number_input("Sugar (g)", min_value=0.0, step=0.1)
        
        with col4:
            notes = st.text_area("Notes", placeholder="Any additional notes about the meal")
        
        # Submit button
        submitted = st.form_submit_button("Save Diet Log")
        
        if submitted:
            # Create diet log
            diet_log = {
                'meal_type': meal_type,
                'food_items': [item.strip() for item in food_items.split('\n') if item.strip()],
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fats': fats,
                'fiber': fiber,
                'sugar': sugar,
                'notes': notes
            }
            
            # Save diet log
            logger = SessionLogger()
            if logger.log_session(
                user_id=user_id,
                diet_log=diet_log
            ):
                st.success("Diet log saved successfully!")
            else:
                st.error("Error saving diet log")

# Analysis Tab
with tabs[3]:
    st.header("📈 Analysis")
    
    # Load all data for analysis
    with get_db_connection() as conn:
        analysis_df = pd.read_sql_query("""
            SELECT s.*, lc.*, je.*, dl.*
            FROM sessions s
            LEFT JOIN lifestyle_context lc ON s.id = lc.session_id
            LEFT JOIN journal_entries je ON s.id = je.session_id
            LEFT JOIN diet_log dl ON s.id = dl.session_id
            WHERE s.user_id = ?
        """, conn, params=(user_id,))
    
    if not analysis_df.empty:
        # Correlation Analysis
        st.subheader("Correlation Analysis")
        
        # Select metrics to analyze
        metrics = st.multiselect(
            "Select metrics to analyze",
            ["mood_score", "focus_score", "mental_clarity", "energy_level", 
             "stress_level", "productivity_score", "sleep_quality"],
            default=["mood_score", "focus_score", "mental_clarity"]
        )
        
        if metrics:
            # Calculate correlations
            corr_matrix = analysis_df[metrics].corr()
            
            # Display correlation matrix
            st.write("Correlation Matrix")
            st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlBu'))
            
            # Display correlation heatmap
            st.write("Correlation Heatmap")
            st.line_chart(corr_matrix)
        
        # Diet Analysis
        st.subheader("Diet Analysis")
        
        if 'calories' in analysis_df.columns:
            # Daily calorie intake
            st.write("Daily Calorie Intake")
            st.line_chart(analysis_df.set_index('timestamp')['calories'])
            
            # Macronutrient distribution
            if all(col in analysis_df.columns for col in ['protein', 'carbs', 'fats']):
                st.write("Macronutrient Distribution")
                macronutrients = analysis_df[['protein', 'carbs', 'fats']].mean()
                st.bar_chart(macronutrients)
        
        # Journal Analysis
        st.subheader("Journal Analysis")
        
        if 'mood' in analysis_df.columns:
            # Mood distribution
            st.write("Mood Distribution")
            mood_counts = analysis_df['mood'].value_counts()
            st.bar_chart(mood_counts)
            
            # Energy and Stress Levels
            if all(col in analysis_df.columns for col in ['energy_level', 'stress_level']):
                st.write("Energy vs Stress Levels")
                energy_stress = analysis_df[['energy_level', 'stress_level']].mean()
                st.bar_chart(energy_stress)

# Recommendations Tab
with tabs[4]:
    st.header("💡 Personalized Recommendations")
    
    # Load all data for analysis
    with get_db_connection() as conn:
        try:
            analysis_df = pd.read_sql_query("""
                SELECT 
                    s.timestamp,
                    lc.sleep_hours,
                    lc.sleep_quality,
                    lc.last_meal_type,
                    lc.hours_since_meal,
                    lc.meal_size,
                    lc.meal_quality,
                    lc.hydration_level,
                    lc.caffeine_intake,
                    lc.exercise_type,
                    lc.exercise_duration_mins,
                    lc.mood_score,
                    lc.focus_score,
                    lc.mental_clarity,
                    lc.activity_type,
                    lc.time_of_day,
                    je.energy_level,
                    je.productivity_score,
                    dl.meal_type as diet_meal_type,
                    dl.calories,
                    dl.protein,
                    dl.carbs,
                    dl.fats
                FROM sessions s
                LEFT JOIN lifestyle_context lc ON s.id = lc.session_id
                LEFT JOIN journal_entries je ON s.id = je.session_id
                LEFT JOIN diet_log dl ON s.id = dl.session_id
                WHERE s.user_id = ?
            """, conn, params=(user_id,))
            
            if not analysis_df.empty:
                # Quick Wins Section
                st.subheader("🎯 Quick Wins")
                col1, col2, col3 = st.columns(3)
                
                # Calculate average metrics
                avg_focus = analysis_df['focus_score'].mean()
                avg_clarity = analysis_df['mental_clarity'].mean()
                avg_mood = analysis_df['mood_score'].mean()
                
                # Focus Quick Win
                with col1:
                    st.metric(
                        "Focus Score",
                        f"{avg_focus:.1f}/5",
                        delta=f"{avg_focus - 3:.1f}",
                        delta_color="normal"
                    )
                    if avg_focus < 3.5:
                        st.info("Try 25-minute focused work sessions with 5-minute breaks")
                
                # Mental Clarity Quick Win
                with col2:
                    st.metric(
                        "Mental Clarity",
                        f"{avg_clarity:.1f}/5",
                        delta=f"{avg_clarity - 3:.1f}",
                        delta_color="normal"
                    )
                    if avg_clarity < 3.5:
                        st.info("Consider reducing caffeine intake after 2 PM")
                
                # Mood Quick Win
                with col3:
                    st.metric(
                        "Mood Score",
                        f"{avg_mood:.1f}/5",
                        delta=f"{avg_mood - 3:.1f}",
                        delta_color="normal"
                    )
                    if avg_mood < 3.5:
                        st.info("Try 10-minute meditation before starting work")
                
                # Optimal Times Section
                st.subheader("⏰ Optimal Times")
                
                # Convert time_of_day to hour
                analysis_df['hour'] = pd.to_datetime(analysis_df['time_of_day'], format='%H:%M', errors='coerce').dt.hour
                
                # Calculate best times for different activities
                activity_times = {}
                for activity in ['deep_work', 'creative', 'learning', 'rest']:
                    activity_data = analysis_df[analysis_df['activity_type'] == activity]
                    if not activity_data.empty:
                        best_hour = activity_data.groupby('hour').agg({
                            'focus_score': 'mean',
                            'mental_clarity': 'mean',
                            'productivity_score': 'mean'
                        }).mean(axis=1).idxmax()
                        
                        activity_times[activity] = {
                            'hour': best_hour,
                            'score': activity_data.groupby('hour').agg({
                                'focus_score': 'mean',
                                'mental_clarity': 'mean',
                                'productivity_score': 'mean'
                            }).mean(axis=1).max()
                        }
                
                # Display optimal times in a more user-friendly format
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Best Times for Different Activities**")
                    for activity, data in activity_times.items():
                        try:
                            hour = int(data['hour'])  # Ensure hour is an integer
                            score = float(data['score'])  # Ensure score is a float
                            confidence = "High" if score > 4 else "Medium" if score > 3 else "Low"
                            
                            st.write(f"**{activity.replace('_', ' ').title()}**")
                            st.write(f"🕒 {hour:02d}:00 - {(hour+2)%24:02d}:00")  # Handle hour wrapping
                            st.write(f"Confidence: {confidence}")
                            st.progress(min(score/5, 1.0))  # Ensure progress bar doesn't exceed 1.0
                            st.write("---")
                        except (ValueError, TypeError) as e:
                            st.warning(f"Could not process optimal time for {activity}: {str(e)}")
                            continue
                
                with col2:
                    try:
                        # Create a heatmap of performance by hour
                        hourly_performance = analysis_df.groupby('hour').agg({
                            'focus_score': 'mean',
                            'mental_clarity': 'mean',
                            'productivity_score': 'mean'
                        }).mean(axis=1)
                        
                        # Ensure all hours are present (0-23)
                        all_hours = pd.Series(index=range(24), dtype=float)
                        hourly_performance = hourly_performance.reindex(all_hours.index, fill_value=0)
                        
                        # Create a color-coded heatmap
                        fig = go.Figure(data=go.Heatmap(
                            z=[hourly_performance.values],
                            x=hourly_performance.index,
                            y=['Performance'],
                            colorscale='RdYlGn',
                            showscale=True
                        ))
                        
                        fig.update_layout(
                            title="Performance by Hour",
                            xaxis_title="Hour of Day",
                            height=200
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not generate performance heatmap: {str(e)}")
                
                # Lifestyle Recommendations
                st.subheader("🌱 Lifestyle Recommendations")
                
                # Sleep Analysis
                if 'sleep_hours' in analysis_df.columns:
                    best_sleep = analysis_df.groupby('sleep_hours').agg({
                        'focus_score': 'mean',
                        'mental_clarity': 'mean',
                        'productivity_score': 'mean'
                    }).mean(axis=1).idxmax()
                    
                    current_sleep = analysis_df['sleep_hours'].mean()
                    
                    st.write("**Sleep Optimization**")
                    if abs(current_sleep - best_sleep) > 0.5:
                        st.warning(f"Your average sleep ({current_sleep:.1f}h) differs from optimal ({best_sleep:.1f}h)")
                    else:
                        st.success(f"Your sleep duration is optimal at {current_sleep:.1f} hours")
                
                # Exercise Analysis
                if 'exercise_type' in analysis_df.columns:
                    best_exercise = analysis_df.groupby('exercise_type').agg({
                        'focus_score': 'mean',
                        'mental_clarity': 'mean',
                        'productivity_score': 'mean'
                    }).mean(axis=1).idxmax()
                    
                    st.write("**Exercise Impact**")
                    st.write(f"Most effective exercise type: {best_exercise.title()}")
                
                # Diet Analysis
                if 'diet_meal_type' in analysis_df.columns:
                    best_meal = analysis_df.groupby('diet_meal_type').agg({
                        'focus_score': 'mean',
                        'mental_clarity': 'mean',
                        'productivity_score': 'mean'
                    }).mean(axis=1).idxmax()
                    
                    st.write("**Diet Optimization**")
                    st.write(f"Most effective meal type: {best_meal.title()}")
                
                # Action Items
                st.subheader("📋 Action Items")
                
                # Generate personalized action items based on the analysis
                action_items = []
                
                # Sleep-related action items
                if 'sleep_hours' in analysis_df.columns and abs(current_sleep - best_sleep) > 0.5:
                    action_items.append(f"Adjust sleep schedule to target {best_sleep:.1f} hours")
                
                # Exercise-related action items
                if 'exercise_type' in analysis_df.columns:
                    action_items.append(f"Incorporate more {best_exercise} into your routine")
                
                # Diet-related action items
                if 'diet_meal_type' in analysis_df.columns:
                    action_items.append(f"Plan more {best_meal} meals during work hours")
                
                # Display action items
                for item in action_items:
                    st.write(f"✅ {item}")
                
        except Exception as e:
            st.error(f"Error loading analysis data: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*NeuroTrack Dashboard - Analyze your brain performance*")
