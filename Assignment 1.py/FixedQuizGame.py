import json

def normalize_answer(ans):
    return set(a.strip().upper() for a in ans.split(",") if a.strip())

# Load questions from JSON file
with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Assignment 1.py/Question.json") as f:
    questions = json.load(f)
    for q in questions:
        q["answers"] = set(q["answers"])
user_scores = {}

def get_grand_champion(scores):
    if not scores:
        return None, 0
    champion = max(scores, key=scores.get)
    return champion, scores[champion]

username = input("Enter your username: ").strip()
print(f"Welcome, {username}!")

high_score = user_scores.get(username, 0)
print(f"Your current high score: {high_score}")

score = 0

for q in questions:
    print(q["question"])
    for opt in q["options"]:
        print(opt)
    user_input = input("Enter your answer(s): ")
    user_answers = normalize_answer(user_input)
    if user_answers == q["answers"]:
        print("Correct!\n")
        score += 1
    else:
        print(f"Incorrect. Correct answer(s): {', '.join(sorted(q['answers']))}\n")

print(f"Your score: {score}/{len(questions)}")