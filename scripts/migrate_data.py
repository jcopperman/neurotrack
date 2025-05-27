import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

def migrate_data():
    """Migrate existing data from CSV files to the database"""
    # Initialize database
    from init_db import create_database
    create_database()
    
    conn = sqlite3.connect('data/neurotrack.db')
    cursor = conn.cursor()
    
    try:
        # Get existing sessions
        cursor.execute('SELECT id, eeg_file_path, context_file_path FROM sessions')
        sessions = cursor.fetchall()
        
        for session_id, eeg_path, context_path in sessions:
            if not eeg_path or not context_path:
                continue
                
            print(f"Migrating session {session_id}...")
            
            # Load EEG data
            try:
                eeg_df = pd.read_csv(eeg_path)
                if 'timestamp' not in eeg_df.columns:
                    # Create timestamps if they don't exist
                    start_time = datetime.now() - pd.Timedelta(seconds=len(eeg_df))
                    eeg_df['timestamp'] = pd.date_range(start=start_time, periods=len(eeg_df), freq='1S')
                
                # Insert EEG data
                eeg_data = list(zip(
                    eeg_df['timestamp'],
                    eeg_df['channel1'],
                    eeg_df['channel2']
                ))
                cursor.executemany('''
                    INSERT INTO eeg_data (session_id, timestamp, channel1, channel2)
                    VALUES (?, ?, ?, ?)
                ''', [(session_id, ts, ch1, ch2) for ts, ch1, ch2 in eeg_data])
                
            except Exception as e:
                print(f"Error migrating EEG data for session {session_id}: {e}")
            
            # Load context data
            try:
                with open(context_path, 'r') as f:
                    context_data = json.load(f)
                
                # Insert context data
                cursor.execute('''
                    INSERT INTO lifestyle_context (
                        session_id, sleep_hours, sleep_quality, last_meal_type,
                        hours_since_meal, meal_size, meal_quality, hydration_level,
                        caffeine_intake, exercise_type, exercise_duration_mins,
                        mood_score, focus_score, mental_clarity, activity_type,
                        time_of_day
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    context_data.get('sleep_hours'),
                    context_data.get('sleep_quality'),
                    context_data.get('last_meal_type'),
                    context_data.get('hours_since_meal'),
                    context_data.get('meal_size'),
                    context_data.get('meal_quality'),
                    context_data.get('hydration_level'),
                    context_data.get('caffeine_intake'),
                    context_data.get('exercise_type'),
                    context_data.get('exercise_duration_mins'),
                    context_data.get('mood_score'),
                    context_data.get('focus_score'),
                    context_data.get('mental_clarity'),
                    context_data.get('activity_type'),
                    context_data.get('time_of_day')
                ))
                
            except Exception as e:
                print(f"Error migrating context data for session {session_id}: {e}")
        
        conn.commit()
        print("Data migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data() 