import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class SessionLogger:
    def __init__(self):
        self.db_path = 'data/neurotrack.db'
        self.ensure_db_exists()

    def ensure_db_exists(self):
        """Ensure the database and its directory exist"""
        Path('data').mkdir(exist_ok=True)
        if not os.path.exists(self.db_path):
            from init_db import create_database
            create_database()

    def log_session(self, user_id, eeg_data=None, context_data=None, journal_entry=None, diet_log=None):
        """
        Log a new session with EEG data and context
        
        Args:
            user_id (int): ID of the user
            eeg_data (list): List of [timestamp, channel1, channel2] readings
            context_data (dict): Dictionary of lifestyle context data
            journal_entry (dict): Dictionary of journal entry data
            diet_log (dict): Dictionary of diet log data
            
        Returns:
            int: ID of the created session
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create session
            cursor.execute('''
                INSERT INTO sessions (user_id, timestamp, notes)
                VALUES (?, ?, ?)
            ''', (user_id, datetime.now(), "Session logged via SessionLogger"))
            session_id = cursor.lastrowid
            
            # Store EEG data if provided
            if eeg_data:
                cursor.executemany('''
                    INSERT INTO eeg_data (session_id, timestamp, channel1, channel2)
                    VALUES (?, ?, ?, ?)
                ''', [(session_id, ts, ch1, ch2) for ts, ch1, ch2 in eeg_data])
            
            # Store context data if provided
            if context_data:
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
            
            # Store journal entry if provided
            if journal_entry:
                cursor.execute('''
                    INSERT INTO journal_entries (
                        session_id, mood, energy_level, stress_level,
                        productivity_score, notes, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    journal_entry.get('mood'),
                    journal_entry.get('energy_level'),
                    journal_entry.get('stress_level'),
                    journal_entry.get('productivity_score'),
                    journal_entry.get('notes'),
                    journal_entry.get('tags')
                ))
            
            # Store diet log if provided
            if diet_log:
                cursor.execute('''
                    INSERT INTO diet_log (
                        session_id, meal_type, food_items, calories,
                        protein, carbs, fats, fiber, sugar, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    diet_log.get('meal_type'),
                    json.dumps(diet_log.get('food_items', [])),
                    diet_log.get('calories'),
                    diet_log.get('protein'),
                    diet_log.get('carbs'),
                    diet_log.get('fats'),
                    diet_log.get('fiber'),
                    diet_log.get('sugar'),
                    diet_log.get('notes')
                ))
            
            conn.commit()
            return session_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_session_data(self, session_id):
        """Retrieve all data for a specific session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get session info
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return None
            
            # Get EEG data
            cursor.execute('SELECT * FROM eeg_data WHERE session_id = ?', (session_id,))
            eeg_data = cursor.fetchall()
            
            # Get context data
            cursor.execute('SELECT * FROM lifestyle_context WHERE session_id = ?', (session_id,))
            context = cursor.fetchone()
            
            # Get journal entry
            cursor.execute('SELECT * FROM journal_entries WHERE session_id = ?', (session_id,))
            journal = cursor.fetchone()
            
            # Get diet log
            cursor.execute('SELECT * FROM diet_log WHERE session_id = ?', (session_id,))
            diet = cursor.fetchone()
            
            return {
                'session': session,
                'eeg_data': eeg_data,
                'context': context,
                'journal': journal,
                'diet': diet
            }
            
        finally:
            conn.close()

if __name__ == "__main__":
    # Example usage
    logger = SessionLogger()
    
    # Sample data
    eeg_data = [
        [datetime.now(), 0.5, 0.3],
        [datetime.now(), 0.6, 0.4]
    ]
    
    context_data = {
        'sleep_hours': 7.5,
        'sleep_quality': 4,
        'last_meal_type': 'balanced',
        'hours_since_meal': 2.5,
        'exercise_type': 'cardio',
        'exercise_duration_mins': 30,
        'mood_score': 4,
        'focus_score': 4,
        'mental_clarity': 4,
        'activity_type': 'deep_work',
        'time_of_day': '09:30',
        'exercise_type': 'cardio',
        'exercise_duration_mins': 30,
        'mood_score': 4
    }
    
    session_id = logger.log_session(1, eeg_data, context_data, "Sample session")
