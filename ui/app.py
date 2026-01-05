import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


# ui/app.py
import streamlit as st
from ui.upload_mode import render_upload_mode
from nlp.agent import FitnessAgent
from nlp.rag_engine import KnowledgeBase
import os

def main():
    st.set_page_config(page_title="AI Fitness Coach", layout="wide")
    st.title("🏋️ AI Fitness Coach (Agentic Edition)")

    # --- SESSION STATE INITIALIZATION ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing_done" not in st.session_state:
        st.session_state.processing_done = False
    if "last_uploaded_file" not in st.session_state:
        st.session_state.last_uploaded_file = None

    tab1, tab2, tab3 = st.tabs(["Live Coach", "Video Analysis", "Chat with Coach"])

    with tab1:
        st.info("Webcam mode is offline. Use 'Video Analysis' tab.")

    with tab2:
        render_upload_mode()

    with tab3:
        st.header("💬 Chat with Coach Alex")
        
        # Guard for API Key and Knowledge Base
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("Please set OPENAI_API_KEY in your .env file")
            return

        # Sidebar button to index PDFs (Do this once)
        if st.sidebar.button("Index Research PDFs"):
            kb = KnowledgeBase(api_key)
            with st.spinner("Reading research papers..."):
                msg = kb.build_knowledge_base()
                st.sidebar.success(msg)

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask Coach Alex about your last set..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                agent = FitnessAgent()
                with st.spinner("Alex is reviewing your biomechanics data..."):
                    response = agent.get_coaching_advice(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()