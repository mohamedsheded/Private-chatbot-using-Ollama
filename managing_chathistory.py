import streamlit as st
from dotenv import load_dotenv  

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory, ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage,trim_messages

# setup the model
model=ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key)

# creating prompt temp
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Answer all questions to the best of your ability in {language}."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# function for creating chat history for each session
store={}
def get_session_history(session_id:str)->BaseChatMessageHistory:
    if session_id not in store:
        store[session_id]=ChatMessageHistory()
    return store[session_id]


#setup the triming strategy
trimmer=trim_messages(
    max_tokens=45,
    strategy="last",
    token_counter=model,
    include_system=True, # include system message
    allow_partial=False,  
    start_on="human"
)



############################################################################################


#creating some history
messages = [
    SystemMessage(content="you're a good assistant"),
    HumanMessage(content="hi! I'm bob"),
    AIMessage(content="hi!"),
    HumanMessage(content="I like vanilla ice cream"),
    AIMessage(content="nice"),
    HumanMessage(content="whats 2 + 2"),
    AIMessage(content="4"),
    HumanMessage(content="thanks"),
    AIMessage(content="no problem!"),
    HumanMessage(content="having fun?"),
    AIMessage(content="yes!"),
]

trimmer.invoke(messages)



from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough

chain=( RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer) | prompt | model )

response=chain.invoke(
    {
    "messages":messages + [HumanMessage(content="What ice cream do i like")],
    "language":"English"
    }
)
response.content



response = chain.invoke(
    {
        "messages": messages + [HumanMessage(content="what math problem did i ask")],
        "language": "English",
    }
)
response.content


## Lets wrap this in the message History
with_message_history = RunnableWithMessageHistory(
                                chain,
                                get_session_history,
                                input_messages_key="messages",
                            )

config={"configurable":{"session_id":"test_chat"}}

response = with_message_history.invoke(
    {
        "messages": messages + [HumanMessage(content="whats my name?")],
        "language": "English",
    },
    config=config,
)

response.content

