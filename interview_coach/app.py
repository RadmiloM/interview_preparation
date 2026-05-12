import streamlit as st
from datetime import datetime
from config import mistral_key, gemini_key, init_llms

if not mistral_key or not gemini_key:
    st.error("⚠️ Missing API keys. Check your .env file.")
    st.stop()

init_llms()
from interview import get_feedback, get_next_question, get_summary

st.title("Interview Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

if st.session_state.interview_started:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    if user_input := st.chat_input("Type your answer...", disabled=st.session_state.interview_finished):
        question = st.session_state.messages[-1]['content']  
        answer = user_input  
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("💬 Generating feedback in progress..."):
                feedback, model_used = get_feedback(question, answer)
        st.session_state.messages.append({"role": "assistant", "content": feedback, "type": "feedback"})
        asked_questions = [message['content'] for message in st.session_state.messages if message.get('type') == 'question']
        if st.session_state.question_count >= 5 and not st.session_state.interview_finished:
            with st.spinner("📝 Generating summary in progress..."):
                whole_summary = get_summary(st.session_state.messages)
                st.session_state.messages.append({"role":"assistant","content":whole_summary, "type":"summary"})
                st.session_state.interview_finished = True
                st.rerun()
        else:
             with st.spinner("🤔 Generating question in progress..."):
                    next_question = get_next_question(st.session_state.role,
                                                      st.session_state.difficulty,
                                                      asked_questions)
             st.session_state.messages.append({"role": "assistant", "content": next_question, "type":"question"})
             st.session_state.question_count+=1
             st.rerun()
else:
    role = st.selectbox("Pick a role: ", [
    "Frontend Developer",
    "Backend Developer",
    "Data Analyst",
    "QA Engineer",
    "DevOps Engineer",
    "HR Manager"
])
    difficulty = st.radio("Pick a difficulty: ", ["Junior", "Mid", "Senior"])
    start_button = st.button("Start an interview")
    if start_button:
        st.session_state.interview_started = True
        st.session_state.role = role
        st.session_state.difficulty = difficulty
        with st.spinner("🤔 Generating question in progress..."):
                question = get_next_question(st.session_state.role, st.session_state.difficulty)
        st.session_state.messages.append({"role": "assistant","content": question, "type": "question"})
        st.session_state.question_count+=1
        st.rerun()

def reset_interview():
        st.session_state.interview_started = False
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.interview_finished = False
        if 'role' in st.session_state:
            del st.session_state.role
        if 'difficulty' in st.session_state:
            del st.session_state.difficulty

if st.session_state.get("interview_finished", False):
    st.write("---") 
    st.success("Interview finished!!")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    role = st.session_state.role.replace(" ", "_")
    difficulty = st.session_state.difficulty
    file_name = f"interview_{role}_{difficulty}_{timestamp}.txt"
    
    summary = next((message['content'] for message in reversed(st.session_state.messages)
                    if message.get("type") =="summary"), None)
    
    if summary:
        st.download_button(
            label="📄 Download Summary",
            data=summary,
            file_name=file_name,
            mime="text/plain"
        )
    st.button("Start New Interview", on_click=reset_interview)