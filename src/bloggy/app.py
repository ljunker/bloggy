from pathlib import Path

from flask import Flask, render_template, abort
import os
import markdown2
import frontmatter
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
POST_DIR = Path(__file__).parent / "posts"
app.config['POST_DIR'] = POST_DIR
MAX_RECENT = 20

def parse_post(filename):
    slug = filename[:-3]
    path = os.path.join(app.config['POST_DIR'], filename)
    with open(path, "r") as f:
        post = frontmatter.load(f)

    date_str = post.get("date", "1970-01-01")
    time_str = post.get("time", "00:00")
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    return {
        "slug": slug,
        "title": post.get("title", slug),
        "datetime": dt,
        "year": dt.year,
        "month": dt.month,
        "content": markdown2.markdown(post.content)
    }

def get_all_posts():
    posts = []
    for filename in os.listdir(app.config['POST_DIR']):
        if filename.endswith(".md"):
            posts.append(parse_post(filename))
    posts.sort(key=lambda p: p['datetime'], reverse=True)
    return posts

@app.route("/")
def index():
    posts = get_all_posts()
    return render_template("index.html", posts=posts[:MAX_RECENT])

@app.route("/<int:year>/<int:month>")
def archive(year, month):
    posts = get_all_posts()
    filtered = [p for p in posts if p["year"] == year and p["month"] == month]
    if not filtered:
        abort(404)
    return render_template("archive.html", posts=filtered, year=year, month=month)

@app.route("/<slug>")
def post(slug):
    filename = f"{slug}.md"
    path = os.path.join(app.config['POST_DIR'], filename)
    if not os.path.exists(path):
        abort(404)
    post = parse_post(filename)
    return render_template("post.html", post=post)

@app.route("/archive")
def archive_overview():
    posts = get_all_posts()
    grouped = defaultdict(list)
    for post in posts:
        grouped[(post["year"], post["month"])].append(post)

    # Sortiert nach Jahr & Monat absteigend
    sorted_groups = sorted(grouped.items(), reverse=True)
    return render_template("archive_overview.html", grouped=sorted_groups)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
