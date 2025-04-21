import os
import pytest
from flask import url_for
from flask_file_explorer.app import create_app, app

@pytest.fixture
def client():
    """Create a test client for the app."""
    # Set up a temporary directory for testing
    test_dir = os.path.dirname(os.path.abspath(__file__))
    app.config['TESTING'] = True
    app.config['BASE_DIR'] = test_dir
    
    with app.test_client() as client:
        yield client

def test_index_redirect(client):
    """Test that the index route redirects to the explore route."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/explore/' in response.location

def test_explore_directory(client):
    """Test that the explore route returns a 200 status code for a directory."""
    response = client.get('/explore/')
    assert response.status_code == 200
    assert b'File Explorer' in response.data

def test_invalid_path(client):
    """Test that the explore route returns a 404 for an invalid path."""
    response = client.get('/explore/does_not_exist')
    assert response.status_code == 404

def test_search_functionality(client):
    """Test the search functionality."""
    # Create a test file
    with open(os.path.join(app.config['BASE_DIR'], 'test_search_file.txt'), 'w') as f:
        f.write('Test content')
    
    # Search for the file
    response = client.get('/explore/?search=test_search')
    assert response.status_code == 200
    assert b'test_search_file.txt' in response.data
    
    # Clean up
    os.remove(os.path.join(app.config['BASE_DIR'], 'test_search_file.txt'))

def test_sorting(client):
    """Test the sorting functionality."""
    response = client.get('/explore/?sort=name&desc=true')
    assert response.status_code == 200
    
    response = client.get('/explore/?sort=modified')
    assert response.status_code == 200
    
    response = client.get('/explore/?sort=size')
    assert response.status_code == 200
