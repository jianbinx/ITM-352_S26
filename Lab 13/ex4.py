from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# Simple HTML templates as strings for demonstration
index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Game</title>
</head>
<body>
    <h1>Welcome to the Quiz Game!</h1>
    <a href="{{ url_for('quiz') }}">Take the Quiz</a><br>
    <a href="{{ url_for('about') }}">About</a>
</body>
</html>
"""

quiz_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Take the Quiz</title>
</head>
<body>
    <h1>Quiz Page</h1>
    <p>This is where the quiz questions will appear.</p>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
"""

about_html = """
<!DOCTYPE html>
<html>
<head>
    <title>About Quiz Game</title>
</head>
<body>
    <h1>About</h1>
    <p>This is a simple quiz game built with Flask.</p>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(index_html)

@app.route("/quiz")
def quiz():
    return render_template_string(quiz_html)

@app.route("/about")
def about():
    return render_template_string(about_html)

if __name__ == "__main__":
    app.run(debug=True)