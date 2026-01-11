# Coordinate scaling, drawing skeletons
# utils/helpers.py
import pandas as pd

def generate_workout_summary():
    """Reads the CSV and creates a small text summary for the AI memory."""
    try:
        df = pd.read_csv("data/logs/workout_log.csv")
        if df.empty: 
            return "No workout data analyzed yet."
        
        total_reps = df['rep_count'].max()
        errors = df[df['error_tag'] != "NONE"]
        
        summary = f"User completed {total_reps} reps. "
        if not errors.empty:
            err_list = errors['error_tag'].unique().tolist()
            summary += f"Issues found: {', '.join(err_list)}. "
            summary += f"Knee angles during errors ranged from {errors['knee_angle'].min()}° to {errors['knee_angle'].max()}°."
        else:
            summary += "The form was perfect across all reps."
        return summary
    except Exception:
        return "No workout data found."