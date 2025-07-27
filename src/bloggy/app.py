from pathlib import Path

from flask import Flask, render_template, abort
import os
import markdown2
import frontmatter
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
POST_DIR = Path(__file__).parent / "posts"
app.config['POST_DIR'] = POST_DIR
MAX_RECENT = 20


def parse_post(filename):
    post_dir_str = str(app.config['POST_DIR'])
    if filename.startswith(post_dir_str):
        relative_path = filename[len(post_dir_str):].lstrip(os.sep)
        slug = relative_path[:-3] if relative_path.endswith('.md') else relative_path
    else:
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


def get_all_posts(current_year=None, current_month=None):
    if not current_year:
        current_year = datetime.now().year
    if not current_month:
        current_month = datetime.now().month

    posts = []
    directory = str(app.config['POST_DIR']) + "/" + str(current_year) + "/" + str(current_month)
    if not os.path.exists(directory):
        return []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            posts.append(parse_post(directory + "/" + filename))
    posts.sort(key=lambda p: p['datetime'], reverse=True)
    return posts


@app.route("/")
def index():
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    posts = get_all_posts(current_year, current_month)
    previous = now.replace(day=1)
    previous = previous - timedelta(days=1)
    previous_year = previous.year
    previous_month = previous.month
    previous_posts = get_all_posts(previous_year, previous_month)
    if len(previous_posts) > 0:
        posts.append(previous_posts)
    return render_template("index.html", posts=posts[:MAX_RECENT])


@app.route("/<int:year>/<int:month>")
def archive(year, month):
    posts = get_all_posts(year, month)
    return render_template("archive.html", posts=posts, year=year, month=month)


@app.route("/<year>/<month>/<slug>")
def post(year, month, slug):
    filename = f"{year}/{month}/{slug}.md"
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
    app.run(host="0.0.0.0", port=9000)
