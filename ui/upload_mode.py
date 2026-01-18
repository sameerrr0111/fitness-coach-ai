# ui/upload_mode.py
import streamlit as st
from core.processor import VideoProcessor
from utils.csv_handler import WorkoutLogger
from utils.helpers import generate_workout_summary
import pandas as pd
import os


def render_upload_mode():
    st.subheader("📹 Workout Analysis")
    
    # NEW: Exercise Selection
    exercise = st.radio("Select Exercise:", ["Squat", "Bicep Curl"], horizontal=True)
    
    uploaded_file = st.file_uploader("Upload video", type=["mp4", "mov", "avi"], key="workout_video_uploader")

    if uploaded_file:
        file_key = f"processed_{uploaded_file.name}_{exercise}" # Key includes exercise type

        if file_key not in st.session_state:
            st.session_state.is_analyzing = True
            WorkoutLogger().clear_log()
            frame_placeholder = st.empty()

            processor = VideoProcessor()
            # Pass the exercise type to the processor
            reps, saved_video_path = processor.process_video(
                uploaded_file, 
                exercise_type=exercise, 
                st_frame_placeholder=frame_placeholder
            )

            st.session_state[file_key] = reps
            st.session_state.processed_video_path = saved_video_path
            st.session_state.workout_summary = generate_workout_summary()
            st.session_state.is_analyzing = False
            st.rerun()

        # --- AFTER ANALYSIS UI ---
        # 1. Play the analyzed video on a loop
        if "processed_video_path" in st.session_state:
            st.video(st.session_state.processed_video_path, loop=True, autoplay=True, muted=True)

        # 2. Show logs below the video
        if os.path.exists("data/logs/workout_log.csv"):
            df = pd.read_csv("data/logs/workout_log.csv")
            errors = df[df["error_tag"] != "NONE"].drop_duplicates(subset=["rep_count"])
            st.markdown("### 📊 Form Issue Logs")
            if not errors.empty:
                st.table(errors[["rep_count", "knee_angle", "error_tag"]])
            else:
                st.success("Perfect form! No issues detected.")