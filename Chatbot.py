import streamlit as st
import os
from langchain.chains import APIChain
from langchain_openai import ChatOpenAI

from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chains import APIChain
from langchain_openai import ChatOpenAI


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
    if not canvas_access_token:
        st.info("Please add your canvas access token to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    # Define the tools for the agent to use
    @tool
    def search(query: str):
        """Call APIs to get the information about the user's Leraning Management System (LMS) """
        # This is a placeholder, but don't tell the LLM that...
        headers = {"Authorization": f"Bearer 3755~wwMfVUwUQykmzhDtMRPaKfCWK7he2uX274838GxGt32VyfvnTyF9E8zGt9mRLXc3"}
        graphQLchain = APIChain.from_llm_and_api_docs(
            llm,
            api_docs='https://canvas.ltu.se/doc/api/all_resources.html',
            headers= headers,
            verbose=False,
            limit_to_domains= None,
        )
        response=graphQLchain.invoke(query)
        return response['output']

    tools = [search]
    tool_node = ToolNode(tools)
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}
        
    # Define the function that determines whether to continue or not
    def should_continue(state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END


    # Define a new graph
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.set_entry_point("chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        should_continue,
    )
    graph_builder.add_edge("tools", 'chatbot')
    checkpointer = MemorySaver()
    graph  = graph_builder.compile(checkpointer=checkpointer)


    for event in graph.stream({"messages": [HumanMessage(content=prompt)]},
    config={"configurable": {"thread_id": 42}}):
        for value in event.values():
            st.session_state.messages.append({"role": "assistant", "content": value["messages"][-1].content})
            st.chat_message("assistant").write(value["messages"][-1].content)

