import json

with open("quiz_questions.json", "r") as json_file:
    questions = json.load(json_file)

print(questions)