import random
from llm import invoke_with_fallback
from config import questions
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

    available_questions = [
        question for question in questions[role][difficulty]
        if question not in (asked_questions or [])
    ]

    fallback_question = (
        random.choice(available_questions) if available_questions
        else random.choice(questions[role][difficulty])
    )
    return invoke_with_fallback(messages,fallback=fallback_question)


def get_summary(llm_messages):
    history = "\n".join([f"{message['role']}: {message['content']}" for message in llm_messages])
    messages = [("system", f"Create summary based on whole session {history}"), ("human", "Provide me a summary of the interview session.")]
    return invoke_with_fallback(messages,fallback="I'm having trouble generating the summary. Let's try again!")