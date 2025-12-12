import os
import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory

from chatbot_utility import get_chapter_list
from get_yt_video import get_yt_video

load_dotenv()
DEVICE = os.getenv("DEVICE", "cpu")

working_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(working_dir)

subjects_list = ["Biology"]

# Helpers
def get_vector_db_path(chapter, subject):
    if chapter == "All Chapters":
        return f"{parent_dir}/vector_db/class_12_{subject.lower()}_vector_db"
    return f"{parent_dir}/chapters_vector_db/{chapter}"

def setup_chain(selected_chapter, selected_subject):
    vector_db_path = get_vector_db_path(selected_chapter, selected_subject)
    embeddings = HuggingFaceEmbeddings(model_kwargs={"device": DEVICE})
    vectorstore = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embeddings
    )
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0
    )
    memory = ConversationBufferMemory(
        llm = llm,
        output_key="answer",
        memory_key="chat_history",
        return_messages=True
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        memory = memory,
        chain_type="stuff",
        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k":3}),
        return_source_documents=True,
        get_chat_history =lambda h: h,
        output_key="answer", 
        verbose = True
    )

    return chain

st.set_page_config(
    page_title="StudyPal 📚",
    page_icon=":books:",
    layout="centered",
)

st.title("📚 Study Pal")

# Initialize the chat history and video history as session state in Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "video_history" not in st.session_state:
    st.session_state.video_history = []

selected_subject = st.selectbox(
    label = "Select Subject",
    options = subjects_list,
    index= None
)

if selected_subject:
    chapter_list = get_chapter_list(selected_subject) + ["All Chapters"]

    selected_chapter = st.selectbox(
        label = "Select Chapter",
        options = chapter_list,
        index= 0
    )

    if selected_chapter:
        if st.session_state.get('selected_chapter') != selected_chapter:
            st.session_state.chat_chain = setup_chain(selected_chapter, selected_subject)
        st.session_state.selected_chapter = selected_chapter

# Display previous messages

for idx, message in enumerate(st.session_state.chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and idx < len(st.session_state.video_history):
            video_refs = st.session_state.video_history[idx]
            if video_refs:
                st.markdown("#### Related YouTube Videos:")
                for title, link in video_refs:
                    st.markdown(f"- [{title}]({link})")

# Input field for user's message
user_input = st.chat_input("Ask AI")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.video_history.append([])

    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response = st.session_state.chat_chain({"question": user_input})
        st.markdown(response["answer"])

        search_query = ", ".join(item["content"] for item in st.session_state.chat_history if item["role"] == "user")
        video_titles, video_links = get_yt_video(search_query)

        st.subheader("Related YouTube Videos:")
        video_refs = []
        for i in range(3):
            st.info(f"**{video_titles[i]}**\n\n[Watch Video]({video_links[i]})")
            video_refs.append((video_titles[i], video_links[i]))
        
        st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
        st.session_state.video_history.append(video_refs)