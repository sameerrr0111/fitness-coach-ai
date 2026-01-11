# nlp/agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from nlp.rag_engine import KnowledgeBase

load_dotenv()

class FitnessAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key, temperature=0.7)
        self.kb = KnowledgeBase(api_key)

    def get_coaching_advice(self, user_query, chat_history, workout_summary):
        # 1. Get Biomechanical Knowledge from PDFs (only if query is technical)
        is_technical = any(word in user_query.lower() for word in ["squat", "form", "depth", "pain", "angle", "error", "biomechanics"])
        expert_context = self.kb.query(user_query) if is_technical else "Generic interaction."

        # 2. The "Human Coach" Prompt
        template = """
        You are 'Coach Alex', a friendly, professional, and world-class Biomechanics Coach.
        
        PERSONA:
        - Talk like a human: Use phrases like "Hey there!", "Let's see...", "Good job on that set."
        - Be concise: Don't give a lecture unless asked.
        - Guardrails: You ONLY talk about fitness, biomechanics, and health. If a user asks about apples, movies, or politics, say: 
          "I'd love to help, but I'm specialized in fitness and biomechanics! Let's get back to your training."

        CONTEXT:
        - LAST WORKOUT DATA: {workout_summary}
        - SCIENTIFIC RESEARCH: {expert_knowledge}

        INSTRUCTIONS:
        1. If the user says "Hi" or "Hello", just reply naturally and ask how their training is going. DO NOT analyze data yet.
        2. If they ask about their performance, use the LAST WORKOUT DATA provided.
        3. If they ask "Why" an error matters, use the SCIENTIFIC RESEARCH to explain the biomechanics (e.g., joint shear, lumbar stress).
        4. Remember the conversation history to stay helpful.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}")
        ])

        chain = prompt | self.llm
        
        response = chain.invoke({
            "input": user_query,
            "chat_history": chat_history,
            "workout_summary": workout_summary,
            "expert_knowledge": expert_context
        })
        
        return response.content