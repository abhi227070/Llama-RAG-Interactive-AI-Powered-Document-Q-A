from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import shutil

class VectorStore:
    def __init__(self, google_api_key):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key = google_api_key)
        self.vector_db = None
        

    def create_vector_store(self, text):
        
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(text)
        self.vector_db = FAISS.from_documents(texts, self.embeddings)

    def get_retriever(self):
        return self.vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3}) if self.vector_db else None