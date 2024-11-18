"""
Unit tests for the app module.

This file contains test cases for the Flask app's routes and functionality.
It includes tests for registration, login, audio upload, mood trends,
and deletion of journal entries.
"""

import io
import os
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path  # Added import for Path
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
import pytest
from app import app  # Adjust this import based on your project structure


@pytest.fixture
def app_fixture():
    """
    Fixture to set up the Flask app for testing.

    This fixture configures the app to be in testing mode and sets a test secret key.
    It yields the Flask app instance for use in tests.
    """
    app.config["TESTING"] = True
    app.secret_key = "test_secret_key"
    yield app


@pytest.fixture
def client_fixture(app_fixture):
    """
    Fixture to set up the test client.

    This fixture provides a Flask test client by creating an app context.
    It allows us to make requests to the Flask application without running it.
    """
    with app_fixture.app_context():
        with app_fixture.test_client() as test_client:
            yield test_client


@pytest.fixture
def mock_user_fixture():
    """
    Fixture to provide a mocked user.

    This fixture creates and returns a mocked user with a valid ObjectId and username.
    It also marks the user as authenticated.
    """
    user = MagicMock()
    user.id = str(ObjectId())  # Valid ObjectId as a string
    user.username = "test_user"
    user.is_authenticated = True  # Mark user as logged in
    return user


@patch("app.db")
def test_register(mock_db, client_fixture):
    """
    Test the user registration process.

    This test simulates a registration request with a new user and verifies
    that the user is successfully registered and redirected to the login page.
    """
    client = client_fixture  # Use a local variable to avoid name conflict
    mock_db.users.find_one.return_value = None  # Simulate no existing user
    response = client.post(
        "/register",
        data={
            "username": "new_user",
            "password": "password",
            "repassword": "password",
        },
    )
    assert response.status_code == 302  # Should redirect to login
    assert b"Redirecting..." in response.data


@patch("app.db")
@patch("app.login_user")
def test_login(mock_login_user, mock_db, client_fixture):
    """
    Test the user login process.

    This test simulates a login request and verifies that the user can log in
    successfully and is redirected appropriately.
    """
    client = client_fixture  # Use a local variable to avoid name conflict
    mock_db.users.find_one.return_value = {
        "_id": ObjectId("1234567890abcdef12345678"),
        "username": "test_user",
        "password": generate_password_hash("password"),  # Correctly hashed password
    }

    response = client.post(
        "/login", data={"username": "test_user", "password": "password"}
    )
    assert response.status_code == 302  # Should redirect to index
    assert b"Redirecting..." in response.data

    mock_login_user.assert_called_once()


@patch("app.current_user")
@patch("app.requests.post")
@patch("app.convert_to_pcm_wav")
def test_upload_audio(
    mock_convert, mock_post, mock_current_user, client_fixture, mock_user_fixture
):
    """
    Test the audio upload functionality.

    This test mocks the file upload process, processes the audio, and verifies
    that the file is uploaded and processed correctly.
    """
    client = client_fixture  # Use a local variable to avoid name conflict
    mock_user = mock_user_fixture  # Use a local variable to avoid name conflict
    upload_folder = "./uploads"
    os.makedirs(upload_folder, exist_ok=True)  # Ensure upload folder exists

    try:
        mock_current_user.get_id.return_value = mock_user.id
        # Use Path.touch() to create the file without needing a with statement
        mock_convert.side_effect = lambda input_file, output_file: Path(
            output_file
        ).touch()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        data = {"audio": (io.BytesIO(b"fake audio data"), "fake_audio.wav")}
        response = client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        assert response.status_code == 200
        assert b"File uploaded and processed successfully" in response.data
    finally:
        shutil.rmtree(upload_folder)  # Clean up after the test


@patch("app.current_user")
@patch("app.collection")
def test_mood_trends(mock_collection, mock_current_user, client_fixture, mock_user_fixture):
    """
    Test the mood trends API.

    This test verifies that the mood trends API returns the correct counts for
    positive, negative, and neutral moods.
    """
    client = client_fixture  # Use a local variable to avoid name conflict
    mock_user = mock_user_fixture  # Use a local variable to avoid name conflict
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.count_documents.side_effect = [
        5,
        3,
        2,
    ]  # Positive, Negative, Neutral counts

    response = client.get("/api/mood-trends")
    assert response.status_code == 200
    assert response.json == {"Positive": 5, "Negative": 3, "Neutral": 2}


@patch("app.current_user")
@patch("app.collection")
def test_delete_entry(mock_collection, mock_current_user, client_fixture, mock_user_fixture):
    """
    Test deleting a journal entry.

    This test simulates deleting a journal entry and verifies that the entry
    is deleted successfully.
    """
    client = client_fixture  # Use a local variable to avoid name conflict
    mock_user = mock_user_fixture  # Use a local variable to avoid name conflict
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.delete_one.return_value.deleted_count = 1

    response = client.delete("/delete-journal/1234567890abcdef12345678")
    assert response.status_code == 200
    assert b"Entry deleted successfully" in response.data
