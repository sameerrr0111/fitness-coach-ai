# nlp/rag_engine.py
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class KnowledgeBase:
    def __init__(self, api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.db_path = "data/vector_store/faiss_index"
        self.source_path = "assets/knowledge_base"

    def build_knowledge_base(self):
        """Builds the index if PDFs are present."""
        if not os.path.exists(self.source_path):
            os.makedirs(self.source_path)
            return "Folder created. Please add PDFs."

        # Check if there are actually PDFs in the folder
        pdfs = [f for f in os.listdir(self.source_path) if f.endswith('.pdf')]
        if not pdfs:
            return "No PDFs found in assets/knowledge_base."

        try:
            loader = DirectoryLoader(self.source_path, glob="./*.pdf", loader_cls=PyPDFLoader)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)
            
            vectorstore = FAISS.from_documents(documents=splits, embedding=self.embeddings)
            vectorstore.save_local(self.db_path)
            return "Knowledge Base successfully indexed."
        except Exception as e:
            return f"Error during indexing: {str(e)}"

    def query(self, user_query):
        """Retrieves expert info from your PDFs."""
        if not os.path.exists(self.db_path):
            return "Scientific research papers are currently being processed. Using general knowledge."
        
        vectorstore = FAISS.load_local(
            self.db_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        docs = vectorstore.similarity_search(user_query, k=2)
        return "\n".join([doc.page_content for doc in docs])