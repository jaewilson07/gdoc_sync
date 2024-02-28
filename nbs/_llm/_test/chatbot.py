#!/usr/bin/env python
# coding: utf-8
---
output-file: llm/app.html
---
# In[1]:


# | default_exp llm/chatbot


# In[2]:


# !pip install --upgrade streamlit openai langchain
# !pip install langchain-openai


# In[3]:


# | exporti
from dataclasses import dataclass
from typing import List

import streamlit as st
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler

from domolibrary_extensions.llm import qna

from nbdev.showdoc import patch_to


# In[4]:


# | exporti
def get_llm_response():
    import random
    import time

    # for testing app streaming if not attached to an llm

    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


# # Utils

# In[5]:


# | exporti
def write_message(role, content, save=True, is_stream=False):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """

    # Write to UI
    with st.chat_message(role):
        if is_stream:
            content = st.write_stream(content)

        else:
            st.markdown(content)

    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})


# In[6]:


# |exporti
def handle_submit(message: str, system_prompt=None, is_test: bool = False):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from Neo4j.
    """

    # Handle the response
    with st.spinner("Thinking..."):
        if is_test:
            write_message(
                "assistant", content=get_llm_response(), save=True, is_stream=True
            )
        write_message(
            "assistant",
            content=qna.get_llm_response(message, system_prompt=system_prompt),
            save=True,
            is_stream=True,
        )


# # Session State
# Initialize chat history

# In[7]:


# | exporti
def init_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


# In[8]:


# |exporti
def print_chat_history(default_greeting):
    if st.session_state.messages == []:
        write_message("assistant", default_greeting, save=False)

    for message in st.session_state.messages:
        write_message(message["role"], message["content"], save=False)


# In[9]:


# initialize conversational memory
memory = ConversationBufferWindowMemory(
    memory_key="chat_history", k=5, return_messages=True, output_key="output"
)


# # Main

# In[10]:


# | export
def execute_st_qna_bot(
    page_title="Your own ChatGPT",
    header="Your own QandA Bot 🤖",
    default_greeting="Hello how can I help you?",
    input_prompt="Message QandA Bot",
    system_prompt="You are a helpful QandA Bot specially trained on a platform called Domo, answer requests with short but detailed and accurate responses",
    is_test: bool = False,
    # callbacks : List[BaseCallbackHandler] = None
):
    """call in a py file to define a q and a bot"""

    st.set_page_config(page_title=page_title, page_icon="🤖")
    st.header(header)

    init_state()
    print_chat_history(default_greeting=default_greeting)

    if prompt := st.chat_input(input_prompt):
        write_message("user", prompt, save=True)
        handle_submit(prompt, system_prompt=system_prompt, is_test=is_test)


# In[11]:


# | export
@dataclass
class CharacterBot:
    name: str
    short_description: str

    greeting: str = "Hello human, first off, have you tried googling it?"
    input_prompt: str = "Hi."
    long_description: str = None
    avatar_url: str = None

    @classmethod
    def from_json(cls, obj):
        return cls(
            name=obj["name"],
            short_description=obj["short_description"],
            long_description=obj.get("long_description", None),
            greeting=obj.get("greeting", None),
            avatar_url=obj.get("url", None),
        )


# In[12]:


# | exporti
@patch_to(CharacterBot)
def execute(self: CharacterBot, is_test: bool = False):
    s = {
        "page_title": "f{self.name} QandA Bot",
        "header": "Your QandA Bot 🤖",
        "default_greeting": self.greeting,
        "input_prompt": self.input_prompt,
        "system_prompt": self.long_description,
        "is_test": is_test,
    }

    execute_st_qna_bot(**s)


# In[13]:


# | export
sample_chatbot_thor = CharacterBot.from_json(
    {
        "name": "Thor",
        "short_description": "I'm Thor, devoted fighter for justice & kin.",
        "long_description": "I, Thor, am a valiant warrior, ever-ready to protect realms and loved ones. My heart swells with pride in leadership during tough times. Loyal to friends like Valkyrie, Korg, and Mighty Thor, we've faced foes like God Butcher, Gorr, and defended the innocent.\n\nBelieving in unity, courage, and sacrifice, I find strength in my allies' love and support. As a fighter and father, I cherish my family. Despite challenges, I stand firm in protecting the cosmos and Asgard's prosperity.",
        "greeting": "Greetings, friend! I am Thor, ever-ready to lend my strength to those in need.",
    }
)


# In[14]:


# | hide

import nbdev

nbdev.nbdev_export()


# In[15]:


# !jupyter nbconvert --to script chatbot.ipynb --output ./_test/chatbot

