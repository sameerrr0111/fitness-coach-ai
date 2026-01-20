# utils/csv_handler.py
import pandas as pd
import os
from datetime import datetime

class WorkoutLogger:
    def __init__(self, filename="data/logs/workout_log.csv"):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.isfile(self.filename):
            self.clear_log()

    def clear_log(self):
        # Changed headers to be exercise-agnostic
        df = pd.DataFrame(columns=['timestamp', 'exercise', 'rep_count', 'primary_metric', 'secondary_metric', 'error_tag'])
        df.to_csv(self.filename, index=False)

    def log_rep(self, exercise, rep_count, m1, m2, error_tag):
        data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exercise': exercise,
            'rep_count': rep_count,
            'primary_metric': round(m1, 2),
            'secondary_metric': round(m2, 2),
            'error_tag': error_tag if error_tag else "NONE"
        }
        df = pd.DataFrame([data])
        df.to_csv(self.filename, mode='a', header=False, index=False)