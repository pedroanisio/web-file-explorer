"""
Tests for the Flask File Explorer application.
"""
import os
import tempfile
import shutil
import io
import zipfile
import pytest
from flask import url_for

# Import from the correct module
from src import create_app, app

@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing."""
    test_dir = tempfile.mkdtemp()
    
    # Create some test files and directories
    os.mkdir(os.path.join(test_dir, 'test_dir'))
    with open(os.path.join(test_dir, 'test_file.txt'), 'w') as f:
        f.write('Test content')
    with open(os.path.join(test_dir, 'another_file.txt'), 'w') as f:
        f.write('More test content')
    
    yield test_dir
    
    # Clean up
    shutil.rmtree(test_dir)

@pytest.fixture
def client(temp_test_dir):
    """Create a test client for the app."""
    app.config['TESTING'] = True
    app.config['BASE_DIR'] = temp_test_dir
    
    with app.test_client() as client:
        # Setup application context
        with app.app_context():
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
    
    # Verify test files are displayed
    assert b'test_file.txt' in response.data
    assert b'another_file.txt' in response.data
    assert b'test_dir' in response.data

def test_explore_subdirectory(client, temp_test_dir):
    """Test that exploring a subdirectory works."""
    # Create a file in the test subdirectory
    with open(os.path.join(temp_test_dir, 'test_dir', 'subdir_file.txt'), 'w') as f:
        f.write('Subdirectory test content')
    
    response = client.get('/explore/test_dir')
    assert response.status_code == 200
    assert b'subdir_file.txt' in response.data

def test_download_file(client):
    """Test that requesting a file returns the file for download."""
    response = client.get('/explore/test_file.txt')
    assert response.status_code == 200
    assert b'Test content' in response.data
    assert 'attachment' in response.headers.get('Content-Disposition', '')

def test_invalid_path(client):
    """Test that the explore route returns a 404 for an invalid path."""
    response = client.get('/explore/does_not_exist')
    assert response.status_code == 404

def test_search_functionality(client):
    """Test the search functionality."""
    # Search for 'another' should find another_file.txt but not test_file.txt
    response = client.get('/explore/?search=another')
    assert response.status_code == 200
    assert b'another_file.txt' in response.data
    assert b'test_file.txt' not in response.data

def test_sorting(client):
    """Test the sorting functionality."""
    # Test name sorting
    response = client.get('/explore/?sort=name&desc=true')
    assert response.status_code == 200
    
    # Test modified time sorting
    response = client.get('/explore/?sort=modified')
    assert response.status_code == 200
    
    # Test size sorting
    response = client.get('/explore/?sort=size')
    assert response.status_code == 200

def test_directory_traversal_prevention(client, temp_test_dir):
    """Test that directory traversal attacks are prevented."""
    # Try to access a path outside the base directory
    parent_dir = os.path.dirname(temp_test_dir)
    relative_path = f'../{os.path.basename(parent_dir)}'
    
    response = client.get(f'/explore/{relative_path}')
    assert response.status_code == 403  # Should be forbidden


def test_download_selected_files(client, temp_test_dir):
    """Test downloading multiple selected files as a zip archive."""
    extra_path = os.path.join(temp_test_dir, 'extra.txt')
    with open(extra_path, 'w') as f:
        f.write('extra')

    response = client.post('/download-selected', json={
        'paths': ['test_file.txt', 'another_file.txt', 'extra.txt']
    })
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/zip'

    zip_bytes = io.BytesIO(response.data)
    with zipfile.ZipFile(zip_bytes) as zf:
        assert set(zf.namelist()) >= {
            'test_file.txt',
            'another_file.txt',
            'extra.txt',
        }
