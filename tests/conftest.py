import pytest
from flask import Flask, template_rendered
import os
import tempfile
import shutil
from datetime import datetime
from src.bloggy.app import app as flask_app


@pytest.fixture
def app():
    """Flask Anwendungs-Fixture."""
    flask_app.config.update({
        'TESTING': True,
        'POST_DIR': None  # wird von temp_post_dir überschrieben
    })
    return flask_app


@pytest.fixture
def client(app):
    """Test-Client Fixture."""
    return app.test_client()


@pytest.fixture
def temp_post_dir(app):
    """
    Erstellt ein temporäres Verzeichnis für Test-Posts.
    Räumt nach dem Test automatisch auf.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        app.config['POST_DIR'] = temp_dir
        yield temp_dir


@pytest.fixture
def sample_post():
    """Ein Beispiel-Blogpost mit Metadaten."""
    return """---
title: Test Post
date: 2025-01-01
time: "12:00"
author: Test Author
tags: [test, example]
---
# Test Content

This is a test post content.
"""


@pytest.fixture
def create_post(temp_post_dir):
    """
    Factory-Fixture zum Erstellen von Test-Posts in der year/month-Struktur.
    """
    def _create_post(filename, content):
        path = os.path.join(temp_post_dir, filename)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)  # Stelle sicher, dass das Zielverzeichnis existiert
        with open(path, 'w') as f:
            f.write(content)
        return path
    return _create_post



@pytest.fixture
def populated_blog(create_post, sample_post):
    """
    Erstellt mehrere Test-Posts in der neuen Ordnerstruktur (year/month).
    """
    posts = [
        ('2025/7/post-1.md', sample_post),
        ('2025/7/post-2.md', """---
title: Second Post
date: 2025-07-01
time: "15:30"
---
# Second Post
Content of second post."""),
        ('2025/6/post-3.md', """---
title: Third Post
date: 2025-06-15
time: "09:00"
---
# Third Post
Content of third post.""")
    ]

    created_posts = []
    for filename, content in posts:
        path = create_post(filename, content)  # Ordnerstruktur year/month beachten
        created_posts.append(path)

    return created_posts


@pytest.fixture
def mock_datetime(monkeypatch):
    """
    Fixture zum Mocken des aktuellen Datums für konsistente Tests.
    """
    class MockDateTime:
        @classmethod
        def now(cls):
            return datetime(2025, 7, 23, 12, 0)

    monkeypatch.setattr("src.bloggy.app.datetime", MockDateTime)


@pytest.fixture
def template_renderer(app):
    """
    Fixture zum Testen von Template-Rendering.
    """
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)

    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)