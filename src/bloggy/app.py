from pathlib import Path

from flask import Flask, render_template, abort
import os
import markdown2
import frontmatter
from datetime import datetime, timedelta
from collections import defaultdict

from flask.cli import load_dotenv

app = Flask(__name__)
POST_DIR = os.getenv("POST_DIR")
app.config['POST_DIR'] = POST_DIR
load_dotenv()
app.config['API_KEY'] = os.getenv('API_KEY')
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


def needs_api_key(func):
    from functools import wraps
    from flask import request, jsonify

    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    return decorated_function


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
    posts += previous_posts
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


@app.route("/new-post", methods=["POST"])
@needs_api_key
def new_post():
    from flask import request, jsonify
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Invalid input"}), 400

    title = data['title']
    content = data['content']
    now = datetime.now()
    filename = f"{now.year}/{now.month}/{now.strftime('%Y-%m-%d')}-{title.replace(' ', '-').lower()}.md"
    path = os.path.join(app.config['POST_DIR'], filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('"%H:%M"')
        f.write(
            f"---\ntitle: {title}\ndate: {date}\ntime: {time}\n---\n\n{content}"
        )

    return jsonify({"message": "Post created", "slug": filename[:-3]}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
