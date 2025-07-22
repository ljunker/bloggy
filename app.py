from flask import Flask, render_template, abort
import os
import markdown2
import frontmatter
from datetime import datetime

app = Flask(__name__)
POST_DIR = "posts"

def parse_post(filename):
    slug = filename[:-3]
    path = os.path.join(POST_DIR, filename)
    with open(path, "r") as f:
        post = frontmatter.load(f)

    date_str = post.get("date", "1970-01-01")
    time_str = post.get("time", "00:00")
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    return {
        "slug": slug,
        "title": post.get("title", slug),
        "datetime": dt,
        "content": markdown2.markdown(post.content)
    }

def get_posts():
    posts = []
    for filename in os.listdir(POST_DIR):
        if filename.endswith(".md"):
            posts.append(parse_post(filename))
    posts.sort(key=lambda p: p['datetime'], reverse=True)
    return posts

@app.route("/")
def index():
    posts = get_posts()
    return render_template("index.html", posts=posts)

@app.route("/<slug>")
def post(slug):
    filename = f"{slug}.md"
    path = os.path.join(POST_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    post = parse_post(filename)
    return render_template("post.html", post=post)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
