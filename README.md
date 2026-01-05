# 🏋️ AI Fitness Coach

An Agentic AI Fitness Coach that analyzes workout videos using YOLO-Pose,
detects reps, evaluates squat form, and provides biomechanics-based feedback
using Retrieval-Augmented Generation (RAG).

## Features
- YOLOv8 Pose Estimation
- Rep Counting with State Machine
- Front / Side Camera View Detection
- Real-time Angle Visualization
- CSV Workout Logging
- AI Coaching via LangChain + OpenAI
- Streamlit UI

## Run Locally
```bash
pip install -r requirements.txt
streamlit run ui/app.py
