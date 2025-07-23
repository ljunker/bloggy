from src.bloggy.app import app as flask_app
import os


def test_index_route(client, populated_blog):
    response = client.get('/')
    assert response.status_code == 200


def test_post_route(client, create_post, sample_post):
    create_post("test-post.md", sample_post)
    response = client.get('/test-post')
    assert response.status_code == 200


def test_post_route_404(client, create_post):
    response = client.get('/non-existent')
    assert response.status_code == 404


def test_archive_route(client, populated_blog):
    response = client.get('/2025/1')
    assert response.status_code == 200


def test_archive_route_404(client, populated_blog):
    response = client.get('/2024/1')  # Jahr ohne Posts
    assert response.status_code == 404


def test_archive_overview(client, populated_blog):
    response = client.get('/archive')
    assert response.status_code == 200


def test_post_content(client, create_post, sample_post):
    create_post("test-post.md", sample_post)
    response = client.get('/test-post')
    content = response.get_data(as_text=True)
    assert "Test Content" in content


def test_template_context(client, populated_blog, template_renderer):
    client.get('/')
    template, context = template_renderer[0]
    assert template.name == 'index.html'
    assert 'posts' in context
    assert len(context['posts']) > 0