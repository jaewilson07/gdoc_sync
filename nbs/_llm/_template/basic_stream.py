# https://github.com/langchain-ai/streamlit-agent/blob/main/streamlit_agent/basic_streaming.py

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain_openai import ChatOpenAI
import streamlit as st


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)
        print(self.text)


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        ChatMessage(role="assistant", content="How can I help you?")
    ]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input():
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        llm = ChatOpenAI(
            openai_api_base="http://192.168.1.45:1234/v1/",
            openai_api_key="not-needed",
            model="local_model",
        )

        stream = llm.stream(st.session_state.messages)

        response = st.write_stream(stream)
        st.session_state.messages.append(
            ChatMessage(role="assistant", content=response)
        )
