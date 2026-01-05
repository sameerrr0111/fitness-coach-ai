# YOLO-Pose implementation
from ultralytics import YOLO
import cv2

class PoseEstimator:
    def __init__(self, model_path='yolov8n-pose.pt'):
        self.model = YOLO(model_path)

    def get_keypoints(self, frame):
        results = self.model(frame, verbose=False)
        if len(results[0].keypoints) > 0:
            # Get x,y coordinates and confidence scores
            # 5=L_Shoulder, 11=L_Hip, 13=L_Knee, 15=L_Ankle (Indices for YOLO)
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            return keypoints
        return None