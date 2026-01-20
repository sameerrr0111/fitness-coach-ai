import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ui/app.py
import sys
import os
import streamlit as st
from ui.upload_mode import render_upload_mode
from nlp.agent import FitnessAgent
from nlp.rag_engine import KnowledgeBase
from langchain_core.messages import HumanMessage, AIMessage

# Ensure pathing is correct
# ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if ROOT_DIR not in sys.path:
#     sys.path.append(ROOT_DIR)

@st.cache_resource
def startup_indexing():
    """Automatically builds the Knowledge Base on startup if missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Missing API Key"
    
    kb = KnowledgeBase(api_key)
    # If the index folder doesn't exist, build it
    if not os.path.exists(kb.db_path):
        return kb.build_knowledge_base()
    return "Ready"

def main():
    st.set_page_config(page_title="AI Fitness Coach", layout="wide")
    
    # 1. Trigger the startup check
    with st.spinner("Initializing Knowledge Base..."):
        kb_status = startup_indexing()
    
    # Show indexing status only if there's an issue
    if "Error" in kb_status or "Missing" in kb_status:
        st.sidebar.warning(f"KB Status: {kb_status}")
    else:
        st.sidebar.success("🎓 Coach Alex is fully briefed on research.")

    st.title("🏋️ AI Fitness Coach (Agentic Edition)")
    
    # ---------------- SESSION STATE ----------------
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "workout_summary" not in st.session_state:
        st.session_state.workout_summary = "No workout analyzed yet."

    # ---------------- MAIN LAYOUT ----------------
    left, right = st.columns([7, 3], gap="large")

    with left:
        # tab1, tab2 = st.tabs(["🎥 Video Analysis", "⚡ Live Mode"])
        tab1 = st.tabs(["🎥 Video Analysis"])[0]

    with tab1:
        render_upload_mode()

    # with tab2:
    #     st.info("Live coaching coming soon.")

    with right:
        st.markdown("## 💬 Coach Alex")
        st.caption("I'm Alex! Ask me anything about your training.")

        chat_box = st.container(height=500)
        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input("Say 'Hi' to start...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(user_input)

            # Convert history for Agent memory
            chat_history = []
            for m in st.session_state.messages[-5:]:
                if m["role"] == "user": chat_history.append(HumanMessage(content=m["content"]))
                else: chat_history.append(AIMessage(content=m["content"]))

            with chat_box:
                with st.chat_message("assistant"):
                    with st.spinner("Alex is typing..."):
                        agent = FitnessAgent()
                        response = agent.get_coaching_advice(
                            user_input, 
                            chat_history, 
                            st.session_state.workout_summary
                        )
                        st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()