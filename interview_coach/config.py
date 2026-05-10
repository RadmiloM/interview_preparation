from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import os
import json

load_dotenv()

mistral_key = os.getenv("MISTRAL_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not mistral_key or not gemini_key:
    st.error("⚠️ Missing API keys. Check your .env file.")
    st.stop()

llm_mistral = ChatMistralAI(
    model="mistral-small-latest",
    api_key=mistral_key
)

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=gemini_key
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "questions_db", "questions.json"), "r") as file:
    questions = json.load(file)