import sqlite3
import os
from pathlib import Path

def create_database():
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('data/neurotrack.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create eeg_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eeg_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        timestamp TIMESTAMP,
        channel1 FLOAT,
        channel2 FLOAT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    ''')

    # Create lifestyle_context table with enhanced diet tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lifestyle_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        sleep_hours FLOAT,
        sleep_quality INTEGER CHECK(sleep_quality BETWEEN 1 AND 5),
        last_meal_type TEXT CHECK(last_meal_type IN ('balanced', 'high-protein', 'high-carb', 'light', 'skip')),
        hours_since_meal FLOAT,
        meal_size TEXT CHECK(meal_size IN ('small', 'medium', 'large')),
        meal_quality INTEGER CHECK(meal_quality BETWEEN 1 AND 5),
        hydration_level INTEGER CHECK(hydration_level BETWEEN 1 AND 5),
        caffeine_intake INTEGER,
        exercise_type TEXT,
        exercise_duration_mins INTEGER,
        mood_score INTEGER CHECK(mood_score BETWEEN 1 AND 5),
        focus_score INTEGER CHECK(focus_score BETWEEN 1 AND 5),
        mental_clarity INTEGER CHECK(mental_clarity BETWEEN 1 AND 5),
        activity_type TEXT CHECK(activity_type IN ('deep_work', 'creative', 'learning', 'rest', 'other')),
        time_of_day TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    ''')

    # Create journal_entries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mood TEXT,
        energy_level INTEGER CHECK(energy_level BETWEEN 1 AND 5),
        stress_level INTEGER CHECK(stress_level BETWEEN 1 AND 5),
        productivity_score INTEGER CHECK(productivity_score BETWEEN 1 AND 5),
        notes TEXT,
        tags TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    ''')

    # Create diet_log table for detailed meal tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS diet_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
        food_items TEXT,
        calories INTEGER,
        protein FLOAT,
        carbs FLOAT,
        fats FLOAT,
        fiber FLOAT,
        sugar FLOAT,
        notes TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database initialized successfully!") 