# ui/upload_mode.py
import streamlit as st
from core.processor import VideoProcessor
from utils.csv_handler import WorkoutLogger
import pandas as pd
import os

def render_upload_mode():
    st.subheader("Upload Workout Video")
    uploaded_file = st.file_uploader("Choose an MP4 file", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file is not None:
        file_key = f"processed_{uploaded_file.name}"
        
        if file_key not in st.session_state:
            logger = WorkoutLogger()
            logger.clear_log()
            
            # --- ADD VISUALIZATION PLACEHOLDER ---
            st.info("Analyzing Video... Visualizing YOLO-Pose Detection below:")
            frame_placeholder = st.empty() 
            
            processor = VideoProcessor()
            # Pass the placeholder to the function
            total_reps = processor.process_video(uploaded_file, st_frame_placeholder=frame_placeholder)
            
            st.session_state[file_key] = total_reps
            st.success(f"Analysis Complete! Total Reps: {total_reps}")
            st.rerun()

        # Display the Final Summary Report
        st.write("### Final Workout Analysis Report")
        if os.path.exists("data/logs/workout_log.csv"):
            df = pd.read_csv("data/logs/workout_log.csv")
            errors_df = df[df['error_tag'] != "NONE"].drop_duplicates(subset=['rep_count', 'error_tag'])
            if not errors_df.empty:
                st.warning("⚠️ Form Issues Detected:")
                st.table(errors_df[['rep_count', 'knee_angle', 'error_tag']])
            else:
                st.success("Perfect form detected!")
            
            st.info("Go to 'Chat with Coach' to discuss these specific results.")