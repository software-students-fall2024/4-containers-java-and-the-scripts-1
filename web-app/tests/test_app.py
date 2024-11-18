import pytest
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
import io
import os
import shutil
from app import app  # Adjust this import based on your project structure


@pytest.fixture
def test_app():
    """Fixture to set up the Flask app for testing."""
    app.config["TESTING"] = True
    app.secret_key = "test_secret_key"
    yield app


@pytest.fixture
def client(test_app):
    """Fixture to set up the test client."""
    with test_app.app_context():
        with test_app.test_client() as client:
            yield client


@pytest.fixture
def mock_user():
    """Fixture to provide a mocked user."""
    user = MagicMock()
    user.id = str(ObjectId())  # Valid ObjectId as a string
    user.username = "test_user"
    user.is_authenticated = True  # Mark user as logged in
    return user


# Test for the register route
@patch("app.db")
def test_register(mock_db, client):
    mock_db.users.find_one.return_value = None  # Simulate no existing user
    response = client.post(
        "/register",
        data={"username": "new_user", "password": "password", "repassword": "password"},
    )
    assert response.status_code == 302  # Should redirect to login
    assert b"Redirecting..." in response.data


# Test for the login route
@patch("app.db")
@patch("app.login_user")
def test_login(mock_login_user, mock_db, client):
    mock_db.users.find_one.return_value = {
        "_id": ObjectId("1234567890abcdef12345678"),
        "username": "test_user",
        "password": generate_password_hash("password"),  # Correctly hashed password
    }

    response = client.post("/login", data={"username": "test_user", "password": "password"})
    assert response.status_code == 302  # Should redirect to index
    assert b"Redirecting..." in response.data

    mock_login_user.assert_called_once()


# Test for the upload audio route
@patch("app.current_user")
@patch("app.requests.post")
@patch("app.convert_to_pcm_wav")
def test_upload_audio(mock_convert, mock_post, mock_current_user, client, mock_user):
    upload_folder = "./uploads"
    os.makedirs(upload_folder, exist_ok=True)  # Ensure upload folder exists

    try:
        mock_current_user.get_id.return_value = mock_user.id
        mock_convert.side_effect = lambda input_file, output_file: open(output_file, "w").close()  # Mock file creation
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        data = {"audio": (io.BytesIO(b"fake audio data"), "fake_audio.wav")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        assert b"File uploaded and processed successfully" in response.data
    finally:
        shutil.rmtree(upload_folder)  # Clean up after the test


# Test for the mood trends API route
@patch("app.current_user")
@patch("app.collection")
def test_mood_trends(mock_collection, mock_current_user, client, mock_user):
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.count_documents.side_effect = [5, 3, 2]  # Positive, Negative, Neutral counts

    response = client.get("/api/mood-trends")
    assert response.status_code == 200
    assert response.json == {"Positive": 5, "Negative": 3, "Neutral": 2}


@patch("app.current_user")
@patch("app.collection")
def test_recent_entries(mock_collection, mock_current_user, client, mock_user):
    # Mock the current user
    mock_current_user.is_authenticated = True  # Mark user as authenticated
    mock_current_user.get_id.return_value = mock_user.id  # Simulate valid user ID

    # Mock database response
    mock_collection.find.return_value = [
        {
            "_id": ObjectId(),
            "file_name": "test.wav",
            "transcript": "Hello",
            "sentiment": {"mood": "Positive"},
            "timestamp": "2024-11-18 00:00:00",
        }
    ]

    # Simulate API request
    response = client.get("/api/recent-entries")

    # Assert response status and content
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]["file_name"] == "test.wav"




# Test for deleting a journal entry
@patch("app.current_user")
@patch("app.collection")
def test_delete_entry(mock_collection, mock_current_user, client, mock_user):
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.delete_one.return_value.deleted_count = 1

    response = client.delete("/delete-journal/1234567890abcdef12345678")
    assert response.status_code == 200
    assert b"Entry deleted successfully" in response.data
