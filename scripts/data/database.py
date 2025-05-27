import sqlite3
import pandas as pd
from pathlib import Path

def get_db_connection():
    """Create a database connection"""
    db_path = Path(__file__).parent.parent.parent / 'data' / 'neurotrack.db'
    return sqlite3.connect(str(db_path))

def load_session_data():
    """Load all sessions with their context data from the database"""
    conn = get_db_connection()
    query = '''
    SELECT 
        s.id as session_id,
        u.name as user_name,
        s.timestamp,
        s.eeg_file_path,
        s.context_file_path,
        lc.sleep_hours,
        lc.sleep_quality,
        lc.last_meal_type,
        lc.hours_since_meal,
        lc.exercise_type,
        lc.exercise_duration_mins,
        lc.mood_score,
        lc.focus_score,
        lc.mental_clarity,
        lc.activity_type,
        lc.time_of_day
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    JOIN lifestyle_context lc ON s.id = lc.session_id
    ORDER BY s.timestamp DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Convert relative paths to absolute paths
    project_root = Path(__file__).parent.parent.parent
    df['eeg_file_path'] = df['eeg_file_path'].apply(
        lambda x: str(project_root / x) if pd.notna(x) else None
    )
    df['context_file_path'] = df['context_file_path'].apply(
        lambda x: str(project_root / x) if pd.notna(x) else None
    )
    
    return df

def get_session_details(session_id):
    """Get detailed information for a specific session"""
    conn = get_db_connection()
    query = '''
    SELECT *
    FROM sessions s
    JOIN lifestyle_context lc ON s.id = lc.session_id
    WHERE s.id = ?
    '''
    df = pd.read_sql_query(query, conn, params=[session_id])
    conn.close()
    return df.iloc[0] if not df.empty else None