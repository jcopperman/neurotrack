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

            # Create lifestyle context
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
                round(random.uniform(6, 9), 1),
                random.randint(1, 5),
                random.choice(['balanced', 'high-protein', 'high-carb', 'light', 'skip']),
                round(random.uniform(0.5, 4), 1),
                random.choice(['small', 'medium', 'large']),
                random.randint(1, 5),
                random.randint(1, 5),
                random.randint(0, 300),
                random.choice(['cardio', 'strength', 'yoga', 'none']),
                random.randint(0, 60),
                random.randint(1, 5),
                random.randint(1, 5),
                random.randint(1, 5),
                random.choice(['deep_work', 'creative', 'learning', 'rest', 'other']),
                session_time.strftime('%H:%M')
            ))

            # Create journal entry
            cursor.execute('''
                INSERT INTO journal_entries (
                    session_id, mood, energy_level, stress_level,
                    productivity_score, notes, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                random.choice(['focused', 'relaxed', 'energetic', 'tired', 'stressed']),
                random.randint(1, 5),
                random.randint(1, 5),
                random.randint(1, 5),
                f"Sample journal entry for session {_ + 1}",
                'work,focus,creative'
            ))

            # Create diet log
            cursor.execute('''
                INSERT INTO diet_log (
                    session_id, meal_type, food_items, calories,
                    protein, carbs, fats, fiber, sugar, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                random.choice(['breakfast', 'lunch', 'dinner', 'snack']),
                json.dumps(['Sample food 1', 'Sample food 2']),
                random.randint(200, 800),
                round(random.uniform(10, 40), 1),
                round(random.uniform(20, 60), 1),
                round(random.uniform(5, 30), 1),
                round(random.uniform(2, 15), 1),
                round(random.uniform(5, 25), 1),
                "Sample meal notes"
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
