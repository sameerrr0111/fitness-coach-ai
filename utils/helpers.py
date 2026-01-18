# utils/helpers.py
import pandas as pd

def generate_workout_summary():
    """
    Reads the workout CSV and generates a concise summary
    for Coach Alex's memory.
    """
    try:
        df = pd.read_csv("data/logs/workout_log.csv")

        if df.empty:
            return "No workout data analyzed yet."

        summary_parts = []

        # ---------------- BASIC STATS ----------------
        total_reps = df["rep_count"].max()
        summary_parts.append(f"User completed {total_reps} total reps.")

        # ---------------- ERROR ANALYSIS ----------------
        errors = df[df["error_tag"] != "NONE"]

        if errors.empty:
            summary_parts.append("Form was consistent across all reps.")
        else:
            unique_errors = errors["error_tag"].value_counts()

            for err, count in unique_errors.items():
                if err == "ELBOW_SWINGING":
                    summary_parts.append(
                        f"Elbow swung forward on {count} bicep curl reps."
                    )
                elif err == "INCOMPLETE_CONTRACTION":
                    summary_parts.append(
                        f"{count} curls were not fully contracted at the top."
                    )
                elif err == "SHALLOW_SQUAT":
                    summary_parts.append(
                        f"{count} squats were slightly shallow."
                    )
                elif err == "CRITICAL_SHALLOW":
                    summary_parts.append(
                        f"{count} squats lacked sufficient depth."
                    )

        # ---------------- FINAL SUMMARY ----------------
        return " ".join(summary_parts)

    except FileNotFoundError:
        return "Workout log not found yet."
    except Exception as e:
        return f"Workout summary unavailable due to error."
