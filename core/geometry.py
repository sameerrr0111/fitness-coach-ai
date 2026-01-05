# Math logic (angle calculations, error detection)
import numpy as np

def calculate_angle(a, b, c):
    """Calculates the angle between three points (joint coordinates)."""
    a = np.array(a) # First point (e.g., Shoulder)
    b = np.array(b) # Mid point (e.g., Hip)
    c = np.array(c) # End point (e.g., Knee)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def check_squat_form(hip_angle, knee_angle):
    """
    Evaluates the peak depth of a completed repetition.
    """
    feedback = "Good Depth"
    error_tag = "NONE"
    
    # Excellent: Knee angle is 95 degrees or less (Deep)
    if knee_angle <= 95:
        feedback = "Excellent Depth"
        error_tag = "NONE"
    
    # Shallow: Stopped between 96 and 115 degrees
    elif 95 < knee_angle < 115:
        feedback = "Slightly Shallow"
        error_tag = "SHALLOW_SQUAT"
        
    # Critical: Didn't even reach near parallel
    elif knee_angle >= 115:
        feedback = "Very Shallow"
        error_tag = "CRITICAL_SHALLOW"

    return feedback, error_tag