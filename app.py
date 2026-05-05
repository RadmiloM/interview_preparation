import httpx
import streamlit as st

from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()

llm = ChatMistralAI(
    model="mistral-large-latest",
    api_key=os.getenv("MISTRAL_API_KEY")
)


st.title("Interview Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True
)
def get_feedback(question, answer):
    messages = [
        SystemMessage(f"""
                    You are an interview evaluator.
            Question: {question}
            Candidate's answer: {answer}

        Give brief feedback in 3-4 sentences max covering:
        - What was good
        - What was missing or incorrect
        - One specific improvement""") ]

    response = llm.invoke(messages)
    return response.content

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True
)
def get_next_question(role,difficulty,asked_questions=None):
    question_list = f"\n Do not repeat these questions: {asked_questions}" if asked_questions else ""
    messages = [SystemMessage(f"""You are an interview coach for {role} at {difficulty} level.
    Ask ONE interview question only.
    No explanations, no follow-up probes, no commentary.{question_list}
    Just the question.""")]
    response = llm.invoke(messages)
    return response.content
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True 
)
def get_summary(messages):
    history = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    message = [SystemMessage(f"Create summary based on whole session {history}")] 
    response = llm.invoke(message)
    return response.content

if st.session_state.interview_started:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    if user_input := st.chat_input("Type your answer...", disabled=st.session_state.interview_finished):
        question = st.session_state.messages[-1]['content']  
        answer = user_input  
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Generating feedback in progress..."):
            try:
                feedback = get_feedback(question, answer)
            except httpx.HTTPStatusError as e:
                feedback = "⚠️ Feedback currently unavailable due to high traffic, but let's continue!"
                st.error("Mistral API is not responding. Please check your connection.")
        st.session_state.messages.append({"role": "assistant", "content": feedback, "type": "feedback"})
        asked_questions = [message['content'] for message in st.session_state.messages if message.get('type') == 'question']
        if st.session_state.question_count >= 5 and not st.session_state.interview_finished:
            try:
                whole_summary = get_summary(st.session_state.messages)
            except httpx.HTTPStatusError:
                whole_summary = "🏁 Interview finished! I couldn't generate a summary due to high traffic, but thanks for participating."
                st.warning("Could not generate summary, finishing session.")
            st.session_state.messages.append({"role":"assistant","content":whole_summary})
            st.session_state.interview_finished = True
            st.rerun()
        else:
             with st.spinner("Generating question in progress..."):
                try:
                    next_question = get_next_question(st.session_state.role,st.session_state.difficulty,asked_questions)
                except httpx.HTTPStatusError as e:
                    next_question = "I'm having trouble connecting. Could you please try to refresh or wait a moment?"
                    st.error("Mistral API is not responding. Please check your connection.") 
             st.session_state.messages.append({"role": "assistant", "content": next_question, "type":"question"})
             st.session_state.question_count+=1
             st.rerun()
else:
    role = st.selectbox("Pick a role: ", [
    "Frontend Developer",
    "Backend Developer",
    "Data Analyst",
    "QA Engineer"
])
    difficulty = st.radio("Pick a difficulty: ", ["Junior", "Mid", "Senior"])
    start_button = st.button("Start an interview")
    if start_button:
        st.session_state.interview_started = True
        st.session_state.role = role
        st.session_state.difficulty = difficulty
        with st.spinner("Generating question in progress..."):
            try:
                question = get_next_question(st.session_state.role, st.session_state.difficulty)
            except httpx.HTTPStatusError as e:
                question = "I'm having trouble connecting. Could you please try to refresh or wait a moment?"
                st.error("Mistral API is not responding. Please check your connection.")
        st.session_state.messages.append({"role": "assistant","content": question, "type": "question"})
        st.session_state.question_count+=1
        st.rerun()




def reset_interview():
        st.session_state.interview_started = False
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.interview_finished = False
        print(st.session_state)
        if 'role' in st.session_state:
            del st.session_state.role
        if 'difficulty' in st.session_state:
            del st.session_state.difficulty

if st.session_state.get("interview_finished", False):
    st.write("---") 
    st.success("Interview finished!!")
    st.button("Start New Interview", on_click=reset_interview)