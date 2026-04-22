from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import random
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key in production

# Load questions from JSON file
def load_questions():
  with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Assign 3/questions.json") as f:
    questions = json.load(f)
    return questions

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    difficulty = request.form.get("difficulty")
    questions = load_questions()
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q["options"])
    session["questions"] = questions
    session["current"] = 0
    session["score"] = 0
    session["feedback"] = ""
    session["difficulty"] = difficulty  # Store difficulty in session
    return redirect(url_for("quiz"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "questions" not in session or session["current"] >= len(session["questions"]):
        return redirect(url_for("result"))
    questions = session["questions"]
    current = session["current"]
    score = session["score"]
    feedback = session.get("feedback", "")
    difficulty = session.get("difficulty", "Easy")
    q = questions[current]

    if request.method == "POST":
        selected = request.form.get("answer")
        if not selected:
            flash("Please select an answer before submitting.")
            return render_template("quiz.html", question=q, current=current+1, total=len(questions), score=score, feedback=feedback)
        correct = q["answer"]
        if selected == correct:
            # Adjust score by difficulty
            if difficulty == "Easy":
                score += 1
            elif difficulty == "Medium":
                score += 2
            elif difficulty == "Hard":
                score += 3
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. The correct answer was: {correct}"
        session["score"] = score
        session["current"] = current + 1
        session["feedback"] = feedback
        return redirect(url_for("quiz"))

    show_feedback = feedback if current > 0 else ""
    session["feedback"] = ""
    return render_template("quiz.html", question=q, current=current+1, total=len(questions), score=score, feedback=show_feedback)

@app.route("/result")
def result():
    score = session.get("score", 0)
    total = len(session.get("questions", []))
    return render_template("result.html", score=score, total=total)

if __name__ == "__main__":
    app.run(debug=True)