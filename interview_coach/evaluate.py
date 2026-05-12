import os
import json
from config import init_llms
from datetime import datetime

init_llms()

from interview import get_feedback,evaluate_feedback_quality


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "evaluation_data", "validation_set.json"), "r") as file:
    questions = json.load(file)

results = []
for q in questions:
    for answer_type in ['weak','medium','strong']:
        answer = q['answers'][answer_type]
        llm_feedback, model_used = get_feedback(q['question'],answer)
        llm_feedback_evaluation = evaluate_feedback_quality(q['question'],answer,llm_feedback,answer_type,model_used)
        if llm_feedback_evaluation is not None:
            results.append({
                "model_used": model_used,
                "question": q['question'],
                "answer_type": answer_type,
                "content_score": llm_feedback_evaluation.content_score,
                "content_reason": llm_feedback_evaluation.content_reason,
                "clarity_score": llm_feedback_evaluation.clarity_score,
                "clarity_reason": llm_feedback_evaluation.clarity_reason,
                "structure_score": llm_feedback_evaluation.structure_score,
                "structure_reason": llm_feedback_evaluation.structure_reason,
                "appropriateness_score": llm_feedback_evaluation.appropriateness_score,
                "appropriateness_reason": llm_feedback_evaluation.appropriateness_reason
            })

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
first_item = questions[0]
role = first_item['role'].replace(" ", "_")
difficulty = first_item['difficulty']
file_name = f"evaluation_{role}_{difficulty}_{timestamp}.json"

with open(file_name, 'w') as f:
    json.dump(results, f,indent=2)