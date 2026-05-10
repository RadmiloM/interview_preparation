import random
from llm import invoke_with_fallback
from config import questions
from pydantic import BaseModel, Field
from config import llm_mistral

class FeedbackEvaluation(BaseModel):
    content_score: int = Field(ge=1, le=5)
    content_reason: str
    clarity_score: int = Field(ge=1, le=5)
    clarity_reason: str
    structure_score: int = Field(ge=1, le=5)
    structure_reason: str

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

def evaluate_feedback_quality(question,answer,feedback):
    messages = [("system",f"""
                    You are an feedback judge.
            Question: {question}
            Candidate's answer: {answer}
            Provided feedback: {feedback}

        Evaluate feedback on the scale 1-5 for:
      - Content: Does the feedback accurately assess the technical content of the response?
      - Clarity: Does the feedback provide clear and understandable insights?
      - Structure: Does the feedback cover what was good, what was missing or incorrect, and provide a specific improvement?"""), 
      ("human", "Evaluate feedback provided for the user") ]
    structured_llm = llm_mistral.with_structured_output(FeedbackEvaluation)
    result = structured_llm.invoke(messages)
    return result;

def get_available_questions(role,difficulty,asked_questions=None):
    return [
        question for question in questions[role][difficulty]
        if question not in (asked_questions or [])
    ]

def get_next_question(role, difficulty, asked_questions=None):
    question_list = f"\nDo not repeat these questions: {asked_questions}" if asked_questions else ""
    messages = [
        ("system", f"""You are an interview coach for {role} at {difficulty} level.
Ask ONE interview question only.
No explanations, no follow-up probes, no commentary.{question_list}
Just the question."""),
        ("human", "Ask me one interview question.")
    ]

    available_questions = get_available_questions(role,difficulty,asked_questions)

    fallback_question = (
        random.choice(available_questions) if available_questions
        else random.choice(questions[role][difficulty])
    )
    return invoke_with_fallback(messages,fallback=fallback_question)

def build_fallback_summary(llm_messages):
    return "\n\n".join([
        message['content'] for message in llm_messages 
        if message.get('type') == 'feedback'
    ])
def get_summary(llm_messages):
    history = "\n".join([f"{message['role']}: {message['content']}" for message in llm_messages])
    messages = [("system", f"Create summary based on whole session {history}"), ("human", "Provide me a summary of the interview session.")]
    fallback_summary = build_fallback_summary(llm_messages)
    return invoke_with_fallback(messages,fallback=fallback_summary)