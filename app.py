import streamlit as st
import os
from backend.pdf_loader import PDFLoader
from backend.vector_store import VectorStore
from backend.qa_chain import Model_Chain
import tempfile

# Set up Streamlit page
st.set_page_config(page_title="📄 PDF Chatbot", layout="wide")

# Sidebar with API Key Inputs
st.sidebar.image("https://store.outrightcrm.com/wp-content/uploads/2024/04/images-1.jpg")
st.sidebar.header("🔑 API Keys Setup")
st.sidebar.markdown("Get your API keys from [Google AI Studio](https://aistudio.google.com/) and [NVIDIA AI Endpoints](https://www.nvidia.com/en-in/ai-data-science/foundation-models/)")

google_api_key = st.sidebar.text_input("Google API Key", type="password")
nvidia_api_key = st.sidebar.text_input("NVIDIA API Key", type="password")

# Store API keys in session state
if not google_api_key or not nvidia_api_key:
    st.sidebar.warning("⚠️ Please enter API keys to continue.")
else:
    st.markdown(
        """
        <h1 style="text-align: center; color: #4A90E2;">
            🦙📄 <span style="font-weight: bold;">LlamaRAG:</span> Interactive AI-Powered Document Q&A
        </h1>
        <p style="text-align: center; font-size: 18px; color: #6C757D;">
            💡 Upload your PDF, ask questions, and get instant AI-powered answers with Langchain & RAG!  
            🚀 Powered by NVIDIA AI & Google AI for smart document interactions.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.session_state["google_api_key"] = google_api_key
    st.session_state["nvidia_api_key"] = nvidia_api_key
    st.sidebar.success("✅ API Keys Set!")

    # Initialize backend components
    vector_store = VectorStore(google_api_key)
    qa_chain = Model_Chain(nvidia_api_key)

    # PDF Uploader in Sidebar
    uploaded_file = st.sidebar.file_uploader("📂 Upload a PDF", type="pdf")
    
    if uploaded_file:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name

        pdf_loader = PDFLoader(temp_path)
        text = pdf_loader.load_text()
        
        vector_store.create_vector_store(text)
        retriever = vector_store.get_retriever()
        if retriever:
            qa_chain.create_chain(retriever)

        st.sidebar.success("Processing Complete")
        
        if st.sidebar.button("🗑️ Clear Chat"):
            st.session_state.messages = []

        # Initialize Chat
        if "conversation" not in st.session_state:
            st.session_state.conversation = qa_chain
            st.session_state.messages = []

        # Display Chat
        for message in st.session_state.get("messages", []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question from the PDF:"):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = qa_chain.ask_question(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
