import pytest
from datetime import datetime
import json
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.log_session import SessionLogger

@pytest.fixture
def logger():
    """Create a SessionLogger instance with test database"""
    return SessionLogger()

def test_log_session_basic(logger):
    """Test basic session logging functionality"""
    # Create test data
    user_id = 1
    eeg_data = [
        (datetime.now(), 0.5, 0.3),
        (datetime.now(), 0.4, 0.2)
    ]
    context_data = {
        'sleep_hours': 7.5,
        'sleep_quality': 4,
        'last_meal_type': 'balanced',
        'hours_since_meal': 2.5,
        'exercise_type': 'cardio',
        'exercise_duration_mins': 30,
        'mood_score': 4
    }
    
    # Log session
    session_id = logger.log_session(
        user_id=user_id,
        eeg_data=eeg_data,
        context_data=context_data
    )
    
    # Verify session was created
    assert session_id is not None, "Session ID should not be None"
    
    # Get session data
    session_data = logger.get_session_data(session_id)
    
    # Verify session data
    assert session_data is not None, "Session data should not be None"
    assert session_data['session'] is not None, "Session info should exist"
    assert len(session_data['eeg_data']) == len(eeg_data), "EEG data should match input"
    assert session_data['context'] is not None, "Context data should exist"

def test_log_session_with_journal(logger):
    """Test session logging with journal entry"""
    # Create test data
    user_id = 1
    journal_entry = {
        'mood': 'focused',
        'energy_level': 4,
        'stress_level': 2,
        'productivity_score': 5,
        'notes': 'Test journal entry',
        'tags': 'test,work'
    }
    
    # Log session
    session_id = logger.log_session(
        user_id=user_id,
        journal_entry=journal_entry
    )
    
    # Get session data
    session_data = logger.get_session_data(session_id)
    
    # Verify journal entry
    assert session_data['journal'] is not None, "Journal entry should exist"
    assert session_data['journal'][2] == journal_entry['mood'], "Mood should match"
    assert session_data['journal'][3] == journal_entry['energy_level'], "Energy level should match" 