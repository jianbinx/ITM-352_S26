import json

questions = [
    {
        "question": "Is minecraft a goated game?",
        "options": ["A) Yes", "B) The Best", "C) Nah", "D) Worst"],
        "answers": ["A", "B"]
    },
    {
        "question": "Select all prime numbers.",
        "options": ["A) 2", "B) 4", "C) 5", "D) 9"],
        "answers": ["A", "C"]
    },
    {
        "question": "Which of these are colors in the rainbow?",
        "options": ["A) Red", "B) Black", "C) Blue", "D) Green"],
        "answers": ["A", "C", "D"]
    }
]

with open("quiz_questions.json", "w") as json_file:
    json.dump(questions, json_file, indent=4)

print("Quiz questions saved to quiz_questions.json")