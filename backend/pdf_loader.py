from langchain_community.document_loaders import PyPDFLoader

class PDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_text(self):
        
        loader = PyPDFLoader(file_path = self.file_path)
        docs = loader.load()
        
        return docs
