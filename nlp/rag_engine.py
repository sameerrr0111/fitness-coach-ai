import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class KnowledgeBase:
    def __init__(self, api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.db_path = "data/vector_store/faiss_index"

    def build_knowledge_base(self):
        if not os.path.exists("assets/knowledge_base"):
            os.makedirs("assets/knowledge_base")
            return "Please add PDFs to assets/knowledge_base folder."

        loader = DirectoryLoader("assets/knowledge_base", glob="./*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        vectorstore = FAISS.from_documents(documents=splits, embedding=self.embeddings)
        vectorstore.save_local(self.db_path)
        return "Knowledge base built successfully!"

    def query(self, user_query):
        """Retrieves expert info from your PDFs."""
        if not os.path.exists(self.db_path):
            return "Note: No specific research papers found. Using general knowledge."
        
        # Fixed the 'allow_dangerous_deserialization' for local usage
        vectorstore = FAISS.load_local(
            self.db_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        docs = vectorstore.similarity_search(user_query, k=2)
        return "\n".join([doc.page_content for doc in docs])