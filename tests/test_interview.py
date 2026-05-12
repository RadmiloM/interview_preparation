from interview import get_feedback, get_available_questions, build_fallback_summary
from config import questions
def test_get_feedback_when_input_is_less_than_five_words():
    answer="I am not sure"
    result,model_used = get_feedback("What is CSS?", answer)
    assert result == "Your answer is too brief. Try to elaborate with at least 2-3 sentences covering the key concepts."

def test_get_available_questions_returns_all_when_none_asked ():
    role="Frontend Developer"
    difficulty="Junior"
    asked_questions = []
    result = get_available_questions(role,difficulty,asked_questions)
    assert len(result) == len(questions[role][difficulty])

def test_get_available_questions_returns_questions_not_asked():
    role="QA Engineer"
    difficulty="Mid"
    asked_questions=["How would you design a test strategy for a new feature from scratch?",
                  "What is the difference between unit, integration, and end-to-end testing?"]
    result = get_available_questions(role,difficulty,asked_questions)
    assert len(result) < len(questions[role][difficulty])

def test_get_summary_returns_default_feedback_when_real_summary_is_not_present():
        messages = [
            {"role":"assistant", "content": "Good job!","type":"feedback"},
            {"role":"assistant", "content": "Nice job!", "type": "feedback"}
        ]
        result = build_fallback_summary(messages)
        assert result == "Good job!\n\nNice job!"



