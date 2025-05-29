import pytest
import sqlite3
from pathlib import Path
import os

@pytest.fixture(scope="session")
def test_db_path():
    """Create a test database path"""
    db_path = 'data/test_neurotrack.db'
    # Ensure the data directory exists
    Path('data').mkdir(exist_ok=True)
    # Remove test database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    return db_path

@pytest.fixture(scope="session")
def test_db_connection(test_db_path):
    """Create a test database connection"""
    conn = sqlite3.connect(test_db_path)
    yield conn
    conn.close()
    # Clean up test database after all tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path) 