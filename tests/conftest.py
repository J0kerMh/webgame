import os
import tempfile

import pytest
from application import mongo,create_app
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({
        'TESTING': True
    })

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()




class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='yhma', password='test'):
        return self._client.post(
            '/login',
            data={'name': username, 'pwd': password}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
