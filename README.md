# 🧠 NeuroTrack — Personal EEG Optimization Toolkit

**NeuroTrack** is a local-first data tracking toolkit that lets you combine EEG readings with lifestyle inputs like sleep, diet, and exercise — to understand what makes your brain perform best.

---

Inspired by the DIY EEG Circuit - https://www.instructables.com/DIY-EEG-and-ECG-Circuit/ 

## ✨ Features

- Track EEG recordings from DIY or consumer devices
- Correlate with:
  - Sleep quality
  - Exercise stats
  - Daily meals / nutrition
  - Time of day and routine
- Analyze and discover patterns:
  - Best times for deep work and creative tasks
  - Optimal cognitive performance windows
  - Activity-specific performance patterns
  - EEG-based focus and cognitive state analysis

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/neuroTrack.git
cd neuroTrack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python3 scripts/init_db.py
```

4. (Optional) Generate sample data:
```bash
python3 scripts/seed_data.py
```
This will create 3 test users and populate 30 days of sample EEG sessions with varied lifestyle contexts.

## 📝 Usage

### Logging a Session
Use `scripts/log_session.py` to record new sessions with EEG data and lifestyle context:

```python
from scripts.log_session import SessionLogger

logger = SessionLogger()
session_id = logger.log_session(
    user_id=1,
    eeg_data=your_eeg_data,
    context_data={
        'sleep_hours': 7.5,
        'sleep_quality': 4,
        'last_meal_type': 'balanced',
        'hours_since_meal': 2.5,
        'exercise_type': 'cardio',
        'exercise_duration_mins': 30,
        'mood_score': 4
    }
)
```

### Analyzing Trends
Run the analysis script to generate visualizations and insights:

```bash
python3 scripts/analyze_trends.py
```

