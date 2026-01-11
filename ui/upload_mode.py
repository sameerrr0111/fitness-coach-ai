# ui/upload_mode.py
import streamlit as st
from core.processor import VideoProcessor
from utils.csv_handler import WorkoutLogger
from utils.helpers import generate_workout_summary # Updated import
import pandas as pd
import os

def render_upload_mode():
    st.subheader("📹 Workout Analysis")
    # Added a unique key to fix the Streamlit Duplicate ID error
    uploaded_file = st.file_uploader("Upload your workout video", type=["mp4", "mov", "avi"], key="workout_video_uploader")

    if uploaded_file:
        file_key = f"processed_{uploaded_file.name}"

        if file_key not in st.session_state:
            WorkoutLogger().clear_log()
            frame_placeholder = st.empty()
            processor = VideoProcessor()
            reps = processor.process_video(uploaded_file, st_frame_placeholder=frame_placeholder)

            st.session_state[file_key] = reps
            # Generate summary once and store in global memory
            st.session_state.workout_summary = generate_workout_summary()
            st.rerun()

        if os.path.exists("data/logs/workout_log.csv"):
            df = pd.read_csv("data/logs/workout_log.csv")
            errors = df[df["error_tag"] != "NONE"].drop_duplicates(subset=["rep_count"])
            st.markdown("### 📊 Workout Summary")
            if not errors.empty:
                st.table(errors[["rep_count", "knee_angle", "error_tag"]])
            else:
                st.success("No form issues detected.")