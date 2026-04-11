from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
   <title>Memes'R'Us</title>
   <meta charset="UTF-8" name="viewport" content="width=device-width, initial-scale=0.8">
   <meta http-equiv="refresh" content="10; url=http://127.0.0.1:5000" />
</head>
<body>
    <h1>Wholesome Meme</h1>
    {% if meme_url %}
        <img src="{{ meme_url }}" alt="Meme" style="max-width:500px;"><br>
        <p>Source subreddit: <b>{{ subreddit }}</b></p>
    {% else %}
        <p>Could not retrieve meme.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def meme():
    url = "https://meme-api.com/gimme/wholesomememes"
    try:
        resp = requests.get(url)
        data = resp.json()
        meme_url = data.get("url")
        subreddit = data.get("subreddit")
    except Exception:
        meme_url = None
        subreddit = None
    return render_template_string(HTML_TEMPLATE, meme_url=meme_url, subreddit=subreddit)

if __name__ == "__main__":
    app.run(debug=True)