import pytest
import sqlite3
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.init_db import create_database
from scripts.seed_data import seed_database

@pytest.fixture
def test_db():
    """Create a test database and return its path"""
    db_path = 'data/test_neurotrack.db'
    # Ensure the data directory exists
    Path('data').mkdir(exist_ok=True)
    # Remove test database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    return db_path

def test_database_creation(test_db):
    """Test that database and tables are created correctly"""
    # Create database
    create_database()
    
    # Connect to database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    expected_tables = ['users', 'sessions', 'eeg_data', 'lifestyle_context', 
                      'journal_entries', 'diet_log']
    
    for table in expected_tables:
        assert table in tables, f"Table {table} was not created"
    
    conn.close()

def test_data_seeding(test_db):
    """Test that data seeding works correctly"""
    # Create and seed database
    create_database()
    seed_database()
    
    # Connect to database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Check if users were created
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    assert user_count == 3, "Expected 3 users to be created"
    
    # Check if sessions were created
    cursor.execute("SELECT COUNT(*) FROM sessions")
    session_count = cursor.fetchone()[0]
    assert session_count > 0, "Expected sessions to be created"
    
    conn.close() 