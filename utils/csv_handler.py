# utils/csv_handler.py
import pandas as pd
import os
from datetime import datetime

class WorkoutLogger:
    def __init__(self, filename="data/logs/workout_log.csv"):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.isfile(self.filename):
            self.clear_log() # Create fresh if doesn't exist

    def clear_log(self):
        """Wipes the CSV file and writes only the headers."""
        df = pd.DataFrame(columns=['timestamp', 'exercise', 'rep_count', 'knee_angle', 'hip_angle', 'error_tag'])
        df.to_csv(self.filename, index=False)

    def log_rep(self, exercise, rep_count, knee_angle, hip_angle, error_tag):
        data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exercise': exercise,
            'rep_count': rep_count,
            'knee_angle': round(knee_angle, 2),
            'hip_angle': round(hip_angle, 2),
            'error_tag': error_tag if error_tag else "NONE"
        }
        df = pd.DataFrame([data])
        # We still use 'a' here because we want to log multiple frames *during* one video
        df.to_csv(self.filename, mode='a', header=False, index=False)