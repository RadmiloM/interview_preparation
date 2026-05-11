import os
import json
from config import init_llms

init_llms()

from interview import get_feedback,evaluate_feedback_quality


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "evaluation_data", "validation_set.json"), "r") as file:
    questions = json.load(file)


for q in questions:
    for answer_type in ['weak','medium','strong']:
        answer = q['answers'][answer_type]
        llm_feedback = get_feedback(q['question'],answer)
        llm_feedback_evaluation = evaluate_feedback_quality(q['question'],answer,llm_feedback)
        print(f"Content: {llm_feedback_evaluation.content_score}/5 — {llm_feedback_evaluation.content_reason}")
        print(f"Clarity: {llm_feedback_evaluation.clarity_score}/5 — {llm_feedback_evaluation.clarity_reason}")
        print(f"Structure: {llm_feedback_evaluation.structure_score}/5 — {llm_feedback_evaluation.structure_reason}")