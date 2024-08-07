import streamlit as st
from langchain_core.messages import HumanMessage
from REST_RAG.graph_builder import create_rest_RAG



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

if canvas_access_token and openai_api_key:
    graph = create_rest_RAG(canvas_access_token,option,openai_api_key)

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    if not canvas_access_token:
        st.info("Please add your canvas access token to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)


    response =  graph.invoke({"messages": [HumanMessage(content=prompt)]},config={"configurable": {"thread_id": 45}})
            
    st.session_state.messages.append({"role": "assistant", "content": response["messages"][-1].content})
    st.chat_message("assistant").write(response["messages"][-1].content)

