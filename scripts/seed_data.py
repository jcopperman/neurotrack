import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random
from pathlib import Path

def generate_sample_eeg_data(duration_seconds=300, sampling_rate=256):
    """Generate sample EEG data with realistic patterns."""
    t = np.linspace(0, duration_seconds, duration_seconds * sampling_rate)
    
    # Generate base signals
    alpha = 0.5 * np.sin(2 * np.pi * 10 * t)  # 10 Hz alpha waves
    beta = 0.3 * np.sin(2 * np.pi * 20 * t)   # 20 Hz beta waves
    theta = 0.4 * np.sin(2 * np.pi * 5 * t)   # 5 Hz theta waves
    delta = 0.2 * np.sin(2 * np.pi * 2 * t)   # 2 Hz delta waves
    
    # Add some noise
    noise = np.random.normal(0, 0.1, len(t))
    
    # Combine signals
    channel1 = alpha + beta + noise
    channel2 = theta + delta + noise
    
    return t, channel1, channel2

def seed_database():
    conn = sqlite3.connect('data/neurotrack.db')
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute('DELETE FROM diet_log')
    cursor.execute('DELETE FROM journal_entries')
    cursor.execute('DELETE FROM lifestyle_context')
    cursor.execute('DELETE FROM eeg_data')
    cursor.execute('DELETE FROM sessions')
    cursor.execute('DELETE FROM users')
    conn.commit()

    # Create sample users
    users = [
        ('John Doe',),
        ('Jane Smith',),
        ('Alex Johnson',)
    ]
    cursor.executemany('INSERT INTO users (name) VALUES (?)', users)
    conn.commit()

    # Get user IDs
    cursor.execute('SELECT id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]

    # Generate sessions from January 1, 2024, to May 20, 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 5, 20)
    
    # Define activity patterns for each user
    activity_patterns = {
        'deep_work': {'hours': [9, 14, 16], 'duration': 2},
        'creative': {'hours': [10, 15], 'duration': 3},
        'learning': {'hours': [11, 19], 'duration': 2},
        'rest': {'hours': [13, 17], 'duration': 1}
    }
    
    # Define meal patterns
    meal_patterns = {
        'breakfast': {'hours': [7, 8, 9], 'types': ['balanced', 'high-protein']},
        'lunch': {'hours': [12, 13], 'types': ['balanced', 'high-carb']},
        'dinner': {'hours': [18, 19, 20], 'types': ['balanced', 'high-protein']},
        'snack': {'hours': [10, 15, 16], 'types': ['light']}
    }
    
    for user_id in user_ids:
        # Generate a random number of sessions for this user
        num_sessions = random.randint(50, 100)
        for _ in range(num_sessions):
            # Generate a random timestamp between start_date and end_date
            session_time = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days),
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Determine activity type based on time of day
            hour = session_time.hour
            activity_type = 'other'
            for act, pattern in activity_patterns.items():
                if hour in pattern['hours']:
                    activity_type = act
                    break
            
            # Determine meal type based on time of day
            meal_type = 'snack'
            for meal, pattern in meal_patterns.items():
                if hour in pattern['hours']:
                    meal_type = meal
                    break
            
            # Create session
            cursor.execute('''
                INSERT INTO sessions (user_id, timestamp, notes)
                VALUES (?, ?, ?)
            ''', (user_id, session_time, f"Sample session {_ + 1}"))
            session_id = cursor.lastrowid

            # Generate and store EEG data
            t, channel1, channel2 = generate_sample_eeg_data()
            eeg_data = list(zip(
                [session_time + timedelta(seconds=float(ts)) for ts in t],
                channel1,
                channel2
            ))
            cursor.executemany('''
                INSERT INTO eeg_data (session_id, timestamp, channel1, channel2)
                VALUES (?, ?, ?, ?)
            ''', [(session_id, ts, ch1, ch2) for ts, ch1, ch2 in eeg_data])

            # Generate correlated lifestyle context
            sleep_hours = round(random.uniform(7, 9), 1)  # More realistic sleep range
            sleep_quality = random.randint(3, 5)  # Higher quality sleep
            
            # Generate correlated scores based on activity type and time
            if activity_type == 'deep_work':
                focus_score = random.randint(4, 5)
                mental_clarity = random.randint(3, 5)
            elif activity_type == 'creative':
                focus_score = random.randint(3, 5)
                mental_clarity = random.randint(4, 5)
            elif activity_type == 'learning':
                focus_score = random.randint(3, 5)
                mental_clarity = random.randint(3, 5)
            else:
                focus_score = random.randint(2, 4)
                mental_clarity = random.randint(2, 4)

            # Create lifestyle context with correlated data
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
                sleep_hours,
                sleep_quality,
                random.choice(meal_patterns[meal_type]['types']),
                round(random.uniform(0.5, 4), 1),
                random.choice(['small', 'medium', 'large']),
                random.randint(3, 5),
                random.randint(3, 5),
                random.randint(0, 300),
                random.choice(['cardio', 'strength', 'yoga', 'none']),
                random.randint(0, 60),
                random.randint(3, 5),  # Higher mood scores
                focus_score,
                mental_clarity,
                activity_type,
                session_time.strftime('%H:%M')
            ))

            # Create journal entry with correlated mood
            mood_options = {
                'deep_work': ['focused', 'determined', 'productive'],
                'creative': ['inspired', 'energetic', 'excited'],
                'learning': ['curious', 'engaged', 'motivated'],
                'rest': ['relaxed', 'calm', 'peaceful'],
                'other': ['neutral', 'balanced', 'content']
            }
            
            cursor.execute('''
                INSERT INTO journal_entries (
                    session_id, mood, energy_level, stress_level,
                    productivity_score, notes, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                random.choice(mood_options[activity_type]),
                random.randint(3, 5),  # Higher energy levels
                random.randint(1, 3),  # Lower stress levels
                focus_score,  # Correlate with focus score
                f"Sample journal entry for {activity_type} session",
                f"{activity_type},focus,{meal_type}"
            ))

            # Create diet log with realistic meal data
            meal_calories = {
                'breakfast': (300, 600),
                'lunch': (500, 800),
                'dinner': (600, 900),
                'snack': (100, 300)
            }
            
            calories = random.randint(*meal_calories[meal_type])
            protein = round(calories * random.uniform(0.2, 0.3) / 4, 1)  # 20-30% of calories from protein
            carbs = round(calories * random.uniform(0.4, 0.5) / 4, 1)    # 40-50% of calories from carbs
            fats = round(calories * random.uniform(0.2, 0.3) / 9, 1)     # 20-30% of calories from fats
            
            cursor.execute('''
                INSERT INTO diet_log (
                    session_id, meal_type, food_items, calories,
                    protein, carbs, fats, fiber, sugar, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                meal_type,
                json.dumps([f"{meal_type} item 1", f"{meal_type} item 2"]),
                calories,
                protein,
                carbs,
                fats,
                round(random.uniform(2, 15), 1),
                round(random.uniform(5, 25), 1),
                f"Sample {meal_type} notes"
            ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Initialize database
    import sys
    sys.path.append('.')
    from scripts.init_db import create_database
    create_database()
    
    # Seed the database
    seed_database()
    print("Database seeded successfully!")
