
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

def get_course_ids(prefix,headers):
    url = prefix+"courses"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        courses = response.json()
        course_ids = [course['id'] for course in courses]
        return course_ids
    return []

def create_vectorstore_retriever(headers, url_list, openai_api_key):
    loader = WebBaseLoader(url_list,header_template=headers)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)
    vectorstore  = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})
    return retriever

def create_rest_RAG(canvas_access_token,option,openai_api_key):
    prefix = f"https://canvas.{option.lower()}.se/api/v1/"
    headers = {"Authorization": f"Bearer {canvas_access_token}"}
    course_ids = get_course_ids(prefix,headers)
    modules_urls = [f"{prefix}courses/{course_id}/modules" for course_id in course_ids]
    assignments_urls = [f"{prefix}courses/{course_id}/assignments" for course_id in course_ids]
    quizzes_urls = [f"{prefix}courses/{course_id}/quizzes" for course_id in course_ids]
    list_courses = prefix+"""courses?include[]=needs_grading_count&include[]=syllabus_body&include[]=public_description&include[]=total_scores&include[]=current_grading_period_scores&include[]=grading_periods&include[]=term&include[]=account&include[]=course_progress&include[]=sections&include[]=storage_quota_used_mb&include[]=total_students&include[]=passback_status&include[]=favorites&include[]=teachers&include[]=observed_users&include[]=concluded"""
    account_info = f"{prefix}users/self"
    url_list = [list_courses, account_info] + modules_urls + assignments_urls + quizzes_urls
    retriever = create_vectorstore_retriever(headers,url_list, openai_api_key)
    retriever_tool = create_retriever_tool(
    retriever,
    "Info_retrieval",
    "Use to look up information about the given query from the user. Search correct information to retrieve students' or teacher's information: i.e, information about courses, assignments, accounts, modules, groups, quizzes etc",
    )

    memory = MemorySaver()
    model = ChatOpenAI(openai_api_key = openai_api_key,model="gpt-4o-mini", temperature=0)
    tools = [retriever_tool]

    system = """ 
           You are an expert chatbot who answers the user's question. 
           The "retriever_tool" helps to find students' or teachers' information: i.e., information about courses, assignments, accounts, modules, groups, quizzes etc.
           If you get the proper context from "retriever_tool" then answer the user's question.
           If you are still unaware of the context or question by executing "retriever_tool" then reply " I don't have enough information to answer this question".
         """
    system_prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("placeholder", "{messages}"), ("placeholder", "{agent_scratchpad}")]
    )
    graph = create_react_agent(model, tools=tools,  checkpointer=memory, state_modifier = system_prompt)
    return graph