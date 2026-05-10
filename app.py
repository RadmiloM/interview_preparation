import httpx
import streamlit as st

from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from tenacity import retry, stop_after_attempt, wait_exponential
import json

load_dotenv()

mistral_key = os.getenv("MISTRAL_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not mistral_key or not gemini_key:
    st.error("⚠️ Missing API keys. Check your .env file.")
    st.stop()

llm_mistral = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY")
)

llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", 
                                    api_key=os.getenv("GEMINI_API_KEY"))

with open("questions_db/questions.json",'r') as file:
    questions = json.load(file)
    
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
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_mistral(messages):
    response = llm_mistral.invoke(messages)
    return response.content

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_gemini(messages):
    response = llm_gemini.invoke(messages)
    return response.content

def invoke_with_fallback(messages, fallback=None):
    try:
        return call_mistral(messages)
    except Exception as e:
        print(f"Mistral failed: {type(e).__name__}: {e}")
    
    try:
        return call_gemini(messages)
    except Exception as e:
        print(f"Gemini failed: {type(e).__name__}: {e}")
    
    return fallback

def get_feedback(question, answer):
    answer_words_count = len(answer.split())

    if(answer_words_count < 5):
        return "Your answer is too brief. Try to elaborate with at least 2-3 sentences covering the key concepts."
    
    messages = [("system",f"""
                    You are an interview evaluator.
            Question: {question}
            Candidate's answer: {answer}

        Give brief feedback in 3-4 sentences max covering:
        - What was good
        - What was missing or incorrect
        - One specific improvement"""), ("human", "Provide me a feedback for my response.") ] 
    return invoke_with_fallback(messages, fallback="⚠️ Could not generate feedback at this moment. " \
    "Both AI services are unavailable. Please try submitting your answer again.")
    
def get_next_question(role, difficulty, asked_questions=None):
    question_list = f"\nDo not repeat these questions: {asked_questions}" if asked_questions else ""
    messages = [
        ("system", f"""You are an interview coach for {role} at {difficulty} level.
Ask ONE interview question only.
No explanations, no follow-up probes, no commentary.{question_list}
Just the question."""),
        ("human", "Ask me one interview question.")
    ]
    return invoke_with_fallback(messages,fallback=questions)
      
def get_summary(llm_messages):
    history = "\n".join([f"{m['role']}: {m['content']}" for m in llm_messages])
    messages = [("system", f"Create summary based on whole session {history}"), ("human", "Provide me a summary of the interview session.")]
    return invoke_with_fallback(messages,fallback="I'm having trouble generating the summary. Let's try again!")

if st.session_state.interview_started:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    if user_input := st.chat_input("Type your answer...", disabled=st.session_state.interview_finished):
        question = st.session_state.messages[-1]['content']  
        answer = user_input  
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("💬 Generating feedback in progress..."):
                feedback = get_feedback(question, answer)
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