def normalize_answer(ans):
    # Normalize input: uppercase, strip spaces, split by comma, remove empty
    return set(a.strip().upper() for a in ans.split(",") if a.strip())
## List of questions, each with options and a set of correct answers
questions = [
    {
        "question": "Is minecraft a goated game?",
        "options": ["A) Yes", "B) The Best", "C) Nah", "D) Worst"],
        "answers": {"A", "B"}
    },
    {
        "question": "Select all prime numbers.",
        "options": ["A) 2", "B) 4", "C) 5", "D) 9"],
        "answers": {"A", "C"}
    },
    {
        "question": "Which of these are colors in the rainbow?",
        "options": ["A) Red", "B) Black", "C) Blue", "D) Green"],
        "answers": {"A", "C", "D"}
    }
]

score = 0
# Initial score

# Loop through each question in the quiz
for q in questions:
    print(q["question"])
    for opt in q["options"]:
        print(opt)
    user_input = input("Enter your answer(s)")
    user_answers = normalize_answer(user_input)
    if user_answers == q["answers"]:
        print("Correct!\n")
        score += 1
        #Increment Add score if correct
    else:
        # Show correct answers if user was wrong
        print(f"Incorrect. Correct answer(s): {', '.join(sorted(q['answers']))}\n")

print(f"Your score: {score}/{len(questions)}")
# Print the final score after all questions
