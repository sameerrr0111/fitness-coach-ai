# nlp/agent.py
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from nlp.rag_engine import KnowledgeBase

load_dotenv() # Loads the API key from .env

class FitnessAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)
        self.kb = KnowledgeBase(api_key)
        self.log_path = "data/logs/workout_log.csv"

    def get_coaching_advice(self, user_query):
        # 1. Read the CSV Log
        try:
            df = pd.read_csv(self.log_path)
            # Focus on reps where an error occurred
            recent_errors = df[df['error_tag'] != "NONE"].tail(10).to_string()
            stats = f"Total Frames Analyzed: {len(df)}, Last Rep Count: {df['rep_count'].max()}"
        except Exception as e:
            recent_errors = "No workout data found."
            stats = ""

        # 2. Get Expert Knowledge (RAG)
        expert_context = self.kb.query(user_query)

        # 3. Enhanced "Human-Like" Prompt
        template = """
        You are 'Coach Alex', a world-class Biomechanics Expert and empathetic Fitness Coach.
        
        CONTEXT FROM USER'S RECENT WORKOUT:
        {stats}
        Specific Errors Detected:
        {workout_data}
        
        EXPERT KNOWLEDGE BASE (from research papers):
        {expert_knowledge}
        
        USER'S QUESTION: {question}
        
        COACHING GUIDELINES:
        1. Start by acknowledging their progress. 
        2. If you see 'SHALLOW_SQUAT', explain that going deeper increases muscle recruitment but must be balanced against knee joint shear.
        3. Mention specific biomechanical terms from the knowledge base (e.g., Joint Shear, Lumbar Flexion, L4-L5 compression) when explaining 'Why'.
        4. Give 2 specific "Drills" to fix the issue.
        5. Keep the tone conversational, like a real person in a gym.
        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        response = chain.invoke({
            "stats": stats,
            "workout_data": recent_errors, 
            "expert_knowledge": expert_context,
            "question": user_query
        })
        
        return response.content