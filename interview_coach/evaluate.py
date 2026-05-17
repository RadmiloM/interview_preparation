import os
import json
import argparse
from config import init_llms
from datetime import datetime

init_llms()

from interview import get_feedback,evaluate_feedback_quality


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "evaluation_data", "validation_set.json"), "r") as file:
    questions = json.load(file)

parser = argparse.ArgumentParser(description="Run evaluation. Provide --role and --difficulty before running.")
parser.add_argument("--role",help="Valid roles: Frontend Developer, Backend Developer, " \
"Data Analyst, QA Engineer, DevOps Engineer, HR Manager", required=True)
parser.add_argument("--difficulty", help="Valid difficulties: Junior, Mid, Senior", required=True)
args = parser.parse_args()
role=args.role
difficulty=args.difficulty

filtered_questions_for_evaluation = [q for q in questions if q['role'] == role and q['difficulty'] == difficulty]

if not filtered_questions_for_evaluation:
    print(f"No questions found for role='{args.role}' and difficulty='{args.difficulty}'")
    print("Currently supported: --role 'Frontend Developer' --difficulty Junior")
    exit(1)

results = []
metrics = ['content_score', 'clarity_score', 'structure_score', 'appropriateness_score']
try:
    for q in filtered_questions_for_evaluation:
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
finally:
    if results:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        role = role.replace(" ","_")
        file_name = f"evaluation_{role}_{difficulty}_{timestamp}.json"
        print(f"Saved {len(results)} results to {file_name}")
        with open(os.path.join(BASE_DIR, "evaluation_data", file_name), "w") as file:
            json.dump(results, file,indent=2)
            
        total_expected = len(filtered_questions_for_evaluation) * 3 
        print(f"\n=== Evaluation Summary ({len(results)}/{total_expected} completed) ===")
        for metric in metrics:
            scores = [r[metric] for r in results]
            avg = sum(scores) / len(scores)
            print(f"{metric}: avg={avg:.2f}, min={min(scores)}, max={max(scores)}")


