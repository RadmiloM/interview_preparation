import streamlit as st

from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage

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

def get_next_question(role,difficulty,asked_questions=None):
    question_list = f"\n Do not repeat these questions: {asked_questions}" if asked_questions else ""
    messages = [SystemMessage(f"""You are an interview coach for {role} at {difficulty} level.
    Ask ONE interview question only.
    No explanations, no follow-up probes, no commentary.{question_list}
    Just the question.""")]
    response = llm.invoke(messages)
    return response.content
  
def get_summary(messages):
    message = [SystemMessage(f"Create summary based on whole session {messages}")] 
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
        feedback = get_feedback(question, answer)
        st.session_state.messages.append({"role": "assistant", "content": feedback, "type": "feedback"})
        asked_questions = [message['content'] for message in st.session_state.messages if message.get('type') == 'question']
        st.session_state.question_count+=1
        if st.session_state.question_count >= 2:
            whole_summary = get_summary(st.session_state.messages)
            st.session_state.messages.append({"role":"assistant","content":whole_summary})
            st.session_state.interview_finished = True
            st.rerun()
        else:
             next_question = get_next_question(st.session_state.role,st.session_state.difficulty,asked_questions)
             st.session_state.messages.append({"role": "assistant", "content": next_question, "type":"question"})
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
        question = get_next_question(st.session_state.role, st.session_state.difficulty)
        st.session_state.messages.append({"role": "assistant","content": question, "type": "question"})
        st.session_state.question_count+=1
        st.rerun()



if st.session_state.interview_started:
    if st.button("Restart"):
        st.session_state.interview_started = False
        st.session_state.messages = []
        st.rerun()
