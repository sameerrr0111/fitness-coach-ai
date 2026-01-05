# core/processor.py
import cv2
import tempfile
import streamlit as st
import numpy as np
from core.vision import PoseEstimator
from core.geometry import calculate_angle, check_squat_form
from utils.csv_handler import WorkoutLogger

class VideoProcessor:
    def __init__(self):
        self.detector = PoseEstimator()
        self.logger = WorkoutLogger()
        self.rep_count = 0
        self.stage = "up"
        self.min_knee_angle = 180.0 # Tracks the deepest point reached in a rep

    def process_video(self, uploaded_file, st_frame_placeholder=None):
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # --- FIX 1: RESIZE IMAGE ---
            # Resize to a standard width (e.g., 640px) while maintaining aspect ratio
            width = 640
            ratio = width / frame.shape[1]
            dim = (width, int(frame.shape[0] * ratio))
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            results = self.detector.model(frame, verbose=False)
            annotated_frame = results[0].plot() 
            
            if len(results[0].keypoints) > 0:
                keypoints = results[0].keypoints.xy[0].cpu().numpy()
                
                if len(keypoints) > 15:
                    hip, knee, ankle = keypoints[11], keypoints[13], keypoints[15]
                    k_angle = calculate_angle(hip, knee, ankle)
                    
                    # --- FIX 2: PEAK DEPTH LOGIC ---
                    # 1. Update the deepest angle reached in the current descent
                    if self.stage == "down":
                        if k_angle < self.min_knee_angle:
                            self.min_knee_angle = k_angle

                    # 2. Transition from Standing to Squatting
                    if k_angle < 140 and self.stage == "up":
                        self.stage = "down"
                        self.min_knee_angle = k_angle # Start tracking

                    # 3. Transition from Squatting to Standing (REP COMPLETE)
                    if k_angle > 150 and self.stage == "down":
                        self.stage = "up"
                        self.rep_count += 1
                        
                        # NOW we evaluate the BEST depth achieved during that whole rep
                        feedback, error = check_squat_form(100, self.min_knee_angle)
                        self.logger.log_rep("Squat", self.rep_count, self.min_knee_angle, 0, error)
                        
                        # Reset for next rep
                        self.min_knee_angle = 180.0

                    # VISUAL FEEDBACK (Live)
                    cv2.putText(annotated_frame, f"Live Angle: {int(k_angle)}", 
                                (int(knee[0]) + 10, int(knee[1])), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    cv2.putText(annotated_frame, f"REPS: {self.rep_count}", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            if st_frame_placeholder:
                st_frame_placeholder.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
            
        cap.release()
        return self.rep_count