from datetime import datetime


def test_index_route(client, populated_blog):
    response = client.get('/')
    assert response.status_code == 200


def test_post_route(client, create_post, sample_post):
    create_post("2025/7/test-post.md", sample_post)  # Neuer Pfad
    response = client.get('/2025/7/test-post')  # Angepasste Route
    assert response.status_code == 200


def test_post_route_404(client, create_post):
    response = client.get('/non-existent')
    assert response.status_code == 404


def test_archive_route(client, populated_blog):
    response = client.get('/2025/1')
    assert response.status_code == 200


def test_archive_overview(client, populated_blog):
    response = client.get('/archive')
    assert response.status_code == 200


def test_post_content(client, create_post, sample_post):
    create_post("2025/7/test-post.md", sample_post)  # Neuer Pfad
    response = client.get('/2025/7/test-post')  # Neue Route
    content = response.get_data(as_text=True)
    assert "Test Content" in content


def test_template_context(client, populated_blog, template_renderer):
    client.get('/')
    template, context = template_renderer[0]
    assert template.name == 'index.html'
    assert 'posts' in context
    assert len(context['posts']) > 0


def test_new_post_creation(client, temp_post_dir):
    new_post = {
        "title": "New Post",
        "content": "This is a new post."
    }
    headers = {
        "X-API-Key": "test_api_key"
    }
    response = client.post('/new-post', json=new_post, headers=headers)
    assert response.status_code == 201
    response = client.get(response.json['slug'])
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "This is a new post" in content


def test_rss_feed(client, create_post, sample_post):
    now = datetime.now()
    sample_post = sample_post.replace("2025-01-01", now.strftime("%Y-%m-%d"))
    sample_post = sample_post.replace("Test Post", "Test Post RSS")
    year = now.year
    month = now.month
    create_post(f"{year}/{month}/test-post.md", sample_post)
    response = client.get('/rss')
    assert response.status_code == 200
    assert response.content_type == 'application/rss+xml'
    content = response.get_data(as_text=True)
    assert "<title>Bloggy RSS Feed</title>" in content
    assert "<item>" in content  # Check for at least one item in the feed