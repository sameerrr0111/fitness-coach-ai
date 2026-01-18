# Math logic (angle calculations, error detection)
import numpy as np

def calculate_angle(a, b, c):
    if np.any(a == 0) or np.any(b == 0) or np.any(c == 0):
        return None
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


# def check_deadlift_form(back_angle, hip_angle):
#     """
#     Evaluates deadlift form. 
#     Back Angle is the inclination of the torso (Shoulder to Hip).
#     """
#     feedback = "Good Pull"
#     error_tag = "NONE"

#     # 1. Back Angle Check (Rounded vs Flat)
#     # In a setup, the back should be between 30 and 45 degrees for most people.
#     # If the angle is too high (>60) while hips are low, it's often a 'Squatty Deadlift'.
#     # If the back angle is too low (<20), it puts extreme shear on the L4-L5.
    
#     if back_angle < 25:
#         feedback = "Back too horizontal!"
#         error_tag = "EXCESSIVE_LEAN"
#     elif back_angle > 65:
#         feedback = "Hips too low (Squatty)!"
#         error_tag = "SQUATTY_DEADLIFT"
        
#     return feedback, error_tag    


# --- BICEP CURL LOGIC ---
def check_curl_form(elbow_angle, swing_score):
    """
    elbow_angle: Tightest angle at the top.
    swing_score: Max horizontal elbow drift relative to torso length.
    """
    feedback = "Good Rep"
    error_tag = "NONE"
    
    if elbow_angle > 65: # Slightly more forgiving angle
        feedback = "Bring the weight higher!"
        error_tag = "INCOMPLETE_CONTRACTION"
    
    # NORMALIZED THRESHOLD:
    # 0.0 means the elbow is perfectly under the shoulder.
    # 0.35 means the elbow moved forward by 35% of the torso length.
    # We allow some "natural" float (up to 0.3)
    elif swing_score > 0.38: 
        feedback = "Too much momentum! Pin your elbow."
        error_tag = "ELBOW_SWINGING"
        
    return feedback, error_tag