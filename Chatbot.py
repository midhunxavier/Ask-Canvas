from openai import OpenAI
import streamlit as st

import os
from langchain.chains.openai_functions.openapi import get_openapi_chain
from langchain.chains import APIChain
from langchain.llms import OpenAI as LangchainOpenAI


with st.sidebar:
    canvas_access_token = st.text_input("Canvas Access Token", key="canvas_access_token", type="password")
    "[Get a Canvas Access Token (LTU)](https://canvas.ltu.se/profile/settings)"
    option = st.selectbox(
    "Which university do you belong to?",
    ("LTU", "KTH", "Chalmers", "Umeå"))
    st.write("You selected:", option)
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/midhunxavier/Ask-Canvas)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://laughing-waddle-5v596g6prpvc79wj.github.dev/)"

st.title("💬 Ask "+ option +" Canvas")
st.caption("🚀 A Canvas chatbot powered by MX")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    llm = LangchainOpenAI(api_key=openai_api_key)
    client = OpenAI(api_key=openai_api_key)

    headers = {"Authorization": f"Bearer {canvas_access_token}"}
    chain = APIChain.from_llm_and_api_docs(
        llm,
        api_docs='https://canvas.ltu.se/doc/api/all_resources.html',
        headers=headers,
        verbose=False,
        limit_to_domains=["https://canvas.ltu.se/api/v1/"],
    )
    response = chain.run(st.session_state.messages[-5:])
    msg = response
    #response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)

    #msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
