#Quiz game Third Version
#Name: Jianbin Xiao
#Date: Feb. 24, 2026
#Make Questions a Dictionary, to include options and the correct choice

questions = {
    "What is the capital of France?": {
        "options": ["A) Paris", "B) London", "C) Rome", "D) Berlin"],
        "answer": "A"
    },
    "What is the largest planet in our solar system?": {
        "options": ["A) Earth", "B) Mars", "C) Jupiter", "D) Saturn"],
        "answer": "C"
    },
    "What is the chemical symbol for water?": {
        "options": ["A) H2O", "B) CO2", "C) O2", "D) NaCl"],
        "answer": "A"
    }
}

score = 0
for q, info in questions.items():
    print(q)
    for opt in info["options"]:
        print(opt)
    user_answer = input("Your answer (A/B/C/D): ").upper()
    if user_answer == info["answer"]:
        print("Correct!\n")
        score += 1
    else:
        print("Incorrect.\n")

print(f"Your score: {score}/{len(questions)}")