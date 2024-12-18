import streamlit as st

from dotenv import load_dotenv  # You can use Langfuse or Opik for local and private data
from langchain_ollama import ChatOllama

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory, ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from langchain_core.output_parsers import StrOutputParser

load_dotenv('./../.env')

st.title("Make Your Own Chatbot")
st.write("[Mohamed Sheded's LinkedIn profile](https://www.linkedin.com/in/mohamed-sheded-50078920b/)")

base_url = "http://localhost:11434"  # Ollama local host
model = 'llama2:latest'

user_id = st.text_input("Enter your user ID", "Sheded")

# Create history session state with session_id and connection link
def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")

# # same Function not using SQLChatMessageHistory
# store ={}
# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory
#     return store[session_id]
    

# Initialize app chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Handle "Start New Conversation" button
if st.button("Start New Conversation"):
    st.session_state.chat_history = []  # Clear history of Streamlit app
    history = get_session_history(user_id)
    history.clear()  # Clear history from SQLite database

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# LLM Setup
llm = ChatOllama(base_url=base_url, model=model)

system = SystemMessagePromptTemplate.from_template("You are a helpful assistant.")
human = HumanMessagePromptTemplate.from_template("{input}")

messages = [system, MessagesPlaceholder(variable_name='history'), human]

prompt = ChatPromptTemplate(messages=messages)

chain = prompt | llm | StrOutputParser()

runnable_with_history = RunnableWithMessageHistory(
    chain, 
    get_session_history, 
    input_messages_key='input', 
    history_messages_key='history'
)

# config is for session id , chat is preserved at each session 
# new session id = new chat history
def chat_with_llm(session_id, input):
    for output in runnable_with_history.stream({'input': input}, config={'configurable': {'session_id': session_id}}):
        yield output

# Chat input handling
prompt = st.chat_input("What is up?")

if prompt:
    st.session_state.chat_history.append({'role': 'user', 'content': prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(chat_with_llm(user_id, prompt))

    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
