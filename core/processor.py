# core/processor.py
import cv2
import tempfile
import streamlit as st
import numpy as np
import os
from core.vision import PoseEstimator
from core.geometry import calculate_angle, check_squat_form,check_curl_form,check_press_form
from utils.csv_handler import WorkoutLogger

class VideoProcessor:
    def __init__(self):
        self.detector = PoseEstimator()
        self.logger = WorkoutLogger()

        self.rep_count = 0
        self.stage = "up"               # IMPORTANT
        self.min_knee_angle = 180.0     # Squat depth

        self.peak_val = 180.0           # Curl depth
        self.max_val = 0.0              # Press lockout
        self.max_swing_score = 0.0

    def process_video(self, uploaded_file, exercise_type="Squat", st_frame_placeholder=None):
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = None 
        
        # Setup initial peak values
        if exercise_type == "Squat": self.peak_val = 180.0
        else: self.peak_val = 180.0 # For Curl (tracking min elbow angle)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # (Resize logic)
            width = 640
            frame = cv2.resize(frame, (width, int(frame.shape[0] * (width/frame.shape[1]))))
            
            if out is None:
                h, w, _ = frame.shape
                out = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    cap.get(cv2.CAP_PROP_FPS) or 20.0,
                    (w, h)
                )

            results = self.detector.model(frame, verbose=False)
            annotated_frame = results[0].plot() 
            
            if len(results[0].keypoints) > 0:
                keypoints = results[0].keypoints.xy[0].cpu().numpy()
                conf = results[0].keypoints.conf[0].cpu().numpy()
                
                if len(keypoints) > 15:
                    if exercise_type == "Squat":
                        hip, knee, ankle = keypoints[11], keypoints[13], keypoints[15]
                        k_angle = calculate_angle(hip, knee, ankle)

                        if k_angle:
                            # Track deepest point
                            if self.stage == "down" and k_angle < self.min_knee_angle:
                                self.min_knee_angle = k_angle

                            # Start squat
                            if k_angle < 140 and self.stage == "up":
                                self.stage = "down"
                                self.min_knee_angle = k_angle

                            # Finish squat
                            if k_angle > 150 and self.stage == "down":
                                self.stage = "up"
                                self.rep_count += 1

                                feedback, error = check_squat_form(100, self.min_knee_angle)
                                self.logger.log_rep(
                                    "Squat",
                                    self.rep_count,
                                    self.min_knee_angle,
                                    0,
                                    error
                                )

                                self.min_knee_angle = 180.0

                    elif exercise_type == "Bicep Curl":
                        # 1. AUTO-ARM SELECTION
                        l_score = conf[5] + conf[7] + conf[9]
                        r_score = conf[6] + conf[8] + conf[10]
                        
                        if l_score > r_score:
                            sh, el, hi = keypoints[5], keypoints[7], keypoints[11]
                            wrist = keypoints[9]
                        else:
                            sh, el, hi = keypoints[6], keypoints[8], keypoints[12]
                            wrist = keypoints[10]

                        angle = calculate_angle(sh, el, wrist)
                        
                        if angle:
                            torso_length = np.linalg.norm(sh - hi)
                            if torso_length > 0:
                                current_swing = abs(sh[0] - el[0]) / torso_length
                                
                                # DRAW A HELPER LINE: Shows the "Pinned" position
                                cv2.line(annotated_frame, (int(sh[0]), int(sh[1])), (int(sh[0]), int(hi[1])), (255, 255, 0), 1)
                                
                                if self.stage == "up" and current_swing > self.max_swing_score:
                                    self.max_swing_score = current_swing

                            # 3. STATE MACHINE
                            if angle < 140 and self.stage == "down":
                                self.stage = "up"
                            
                            if self.stage == "up" and angle < self.peak_val:
                                self.peak_val = angle

                            if angle > 155 and self.stage == "up":
                                self.stage = "down"
                                self.rep_count += 1
                                
                                # EVALUATE using Normalized Score
                                feedback, error = check_curl_form(self.peak_val, self.max_swing_score)
                                self.logger.log_rep(exercise_type, self.rep_count, self.peak_val, self.max_swing_score, error)
                                
                                # Reset
                                self.peak_val = 180.0
                                self.max_swing_score = 0.0

                    elif exercise_type == "Overhead Press":
                        # Detect best arm
                        l_score = conf[5] + conf[7] + conf[9]
                        r_score = conf[6] + conf[8] + conf[10]
                        if l_score > r_score:
                            sh, el, wrist = keypoints[5], keypoints[7], keypoints[9]
                        else:
                            sh, el, wrist = keypoints[6], keypoints[8], keypoints[10]
                        
                        angle = calculate_angle(sh, el, wrist)
                        if angle:
                            # Tracking logic
                            if angle > 150 and self.stage == "down": # Moving Up
                                self.stage = "up"
                            
                            if self.stage == "up" and angle > self.max_val:
                                self.max_val = angle # Track best lockout
                            
                            if self.stage == "down" and angle < self.peak_val:
                                self.peak_val = angle # Track best depth

                            if angle < 100 and self.stage == "up": # Back to Bottom
                                self.stage = "down"
                                self.rep_count += 1
                                f, err = check_press_form(self.max_val, self.peak_val)
                                self.logger.log_rep(exercise_type, self.rep_count, self.max_val, self.peak_val, err)
                                # Reset
                                self.max_val = 0.0
                                self.peak_val = 180.0

                    cv2.putText(annotated_frame, f"REPS: {self.rep_count}", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            out.write(annotated_frame)
            if st_frame_placeholder:
                st_frame_placeholder.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
            
        cap.release()
        if out: out.release()
        return self.rep_count, output_path