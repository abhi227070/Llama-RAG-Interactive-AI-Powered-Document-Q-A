from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import streamlit as st

class Model_Chain:
    def __init__(self, nvidia_api_key):
        self.llm = ChatNVIDIA(model="meta/llama-3.1-405b-instruct", nvidia_api_key=nvidia_api_key)
        self.rag_chain = None
        self.history_aware_retriever = None
    

    def create_chain(self, retriever):
        # Contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        self.history_aware_retriever = create_history_aware_retriever(self.llm, retriever, contextualize_q_prompt)

        # QA system prompt
        qa_system_prompt = (
            "You are an assistant for question-answering tasks. Use "
            "the following retrieved context to answer the "
            "question. If you don't know the answer, just say that you "
            "don't know. Use concise responses."
            "{context}"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [("system", qa_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}")]
        ) 

        # Create the question-answering chain
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt) 
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)

    def ask_question(self, query):
        if self.rag_chain:
            chat_history = st.session_state.messages[-2:] if "messages" in st.session_state else []
            response = self.rag_chain.invoke({"input": query, "chat_history": chat_history})

            return response['answer']
        return "No PDF loaded yet!"

    def get_llm(self):
        return self.llm

    def get_retriever(self):
        return self.history_aware_retriever
