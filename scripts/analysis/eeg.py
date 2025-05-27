import numpy as np
import pandas as pd
from scipy import signal
import sqlite3
from datetime import datetime, timedelta
import warnings

def load_eeg_data(session_id):
    """
    Load EEG data from the database for a specific session
    
    Args:
        session_id (int): ID of the session to load
        
    Returns:
        tuple: (timestamps, channel1_data, channel2_data)
    """
    conn = sqlite3.connect('data/neurotrack.db')
    cursor = conn.cursor()
    
    try:
        # Get EEG data for the session
        cursor.execute('''
            SELECT timestamp, channel1, channel2
            FROM eeg_data
            WHERE session_id = ?
            ORDER BY timestamp
        ''', (session_id,))
        
        data = cursor.fetchall()
        if not data:
            return None, None, None
            
        # Convert to numpy arrays
        timestamps = np.array([row[0] for row in data])
        channel1 = np.array([row[1] for row in data])
        channel2 = np.array([row[2] for row in data])
        
        return timestamps, channel1, channel2
        
    finally:
        conn.close()

def analyze_eeg_data(session_id, sampling_rate=256):
    """
    Analyze EEG data for a specific session
    
    Args:
        session_id (int): ID of the session to analyze
        sampling_rate (int): Sampling rate of the EEG data in Hz
        
    Returns:
        dict: Dictionary containing analysis results
    """
    # Load EEG data
    timestamps, channel1, channel2 = load_eeg_data(session_id)
    if timestamps is None:
        return None
        
    # Calculate Welch's periodogram
    nperseg = min(256, len(channel1) // 4)  # Window size
    noverlap = nperseg // 2  # 50% overlap
    
    # Ensure noverlap is less than nperseg
    noverlap = min(noverlap, nperseg - 1)
    
    # Calculate power spectral density
    freqs1, psd1 = signal.welch(channel1, fs=sampling_rate, nperseg=nperseg, noverlap=noverlap)
    freqs2, psd2 = signal.welch(channel2, fs=sampling_rate, nperseg=nperseg, noverlap=noverlap)
    
    # Calculate band powers
    band_powers = calculate_band_powers(freqs1, psd1, freqs2, psd2)
    
    # Calculate cognitive metrics
    cognitive_metrics = calculate_cognitive_metrics(band_powers)
    
    return {
        'band_powers': band_powers,
        'cognitive_metrics': cognitive_metrics,
        'raw_data': {
            'timestamps': timestamps,
            'channel1': channel1,
            'channel2': channel2
        }
    }

def calculate_band_powers(freqs1, psd1, freqs2, psd2):
    """Calculate power in different frequency bands"""
    # Define frequency bands
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 50)
    }
    
    band_powers = {}
    
    for band_name, (low, high) in bands.items():
        # Find indices for the frequency band
        idx = np.logical_and(freqs1 >= low, freqs1 <= high)
        
        # Calculate power in the band for both channels
        power1 = np.trapz(psd1[idx], freqs1[idx])
        power2 = np.trapz(psd2[idx], freqs2[idx])
        
        # Store average power
        band_powers[band_name] = (power1 + power2) / 2
        
    return band_powers

def calculate_cognitive_metrics(band_powers):
    """Calculate cognitive metrics from band powers"""
    # Calculate ratios
    alpha_theta = band_powers['alpha'] / band_powers['theta']
    beta_alpha = band_powers['beta'] / band_powers['alpha']
    
    # Calculate focus score (0-5)
    focus_score = min(5, max(1, 3 + (beta_alpha - 1) * 2))
    
    # Calculate relaxation score (0-5)
    relaxation_score = min(5, max(1, 3 + (alpha_theta - 1) * 2))
    
    # Calculate mental clarity score (0-5)
    clarity_score = min(5, max(1, 3 + (band_powers['alpha'] / (band_powers['theta'] + band_powers['delta'])) * 2))
    
    return {
        'focus_score': round(focus_score, 1),
        'relaxation_score': round(relaxation_score, 1),
        'clarity_score': round(clarity_score, 1)
    }

def check_signal_quality(data):
    """Check EEG signal quality and return True if signal is good enough for analysis"""
    try:
        # Check for flatlines or constant values
        if np.any(np.std(data, axis=0) < 1e-6):
            print("Warning: Channel contains flatline or constant values")
            return False
            
        # Check for extreme values
        if np.any(np.abs(data) > 1000):
            print("Warning: Channel contains extreme values")
            return False
            
        # Check for excessive noise (using rolling standard deviation)
        window = 100  # 100 samples window
        rolling_std = pd.DataFrame(data).rolling(window=window).std()
        if np.any(rolling_std > np.mean(rolling_std) * 5):
            print("Warning: Channel contains excessive noise")
            return False
            
        return True
    except Exception as e:
        print(f"Error in signal quality check: {e}")
        return False