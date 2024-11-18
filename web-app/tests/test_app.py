"""
Unit tests for the Flask app module.

This file contains test cases for the Flask app's routes and functionality.
It includes tests for registration, login, audio upload, mood trends,
recent entries retrieval, and deletion of journal entries.
"""

import io
import os
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path  # Import Path for file operations
import pytest
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from app import app  # Adjust this import based on your project structure


@pytest.fixture(name="app_fixture")
def fixture_app():
    """Fixture to set up the Flask app for testing."""
    app.config["TESTING"] = True
    app.secret_key = "test_secret_key"
    yield app


@pytest.fixture(name="client_fixture")
def fixture_client(app_fixture):
    """Fixture to set up the test client."""
    with app_fixture.app_context():
        with app_fixture.test_client() as test_client:
            yield test_client


@pytest.fixture(name="mock_user_fixture")
def fixture_mock_user():
    """Fixture to provide a mocked user."""
    user = MagicMock()
    user.id = str(ObjectId())
    user.username = "test_user"
    user.is_authenticated = True
    return user


@patch("app.db")
def test_register(mock_db, client_fixture):
    """
    Test the user registration process.

    This test simulates a registration request and verifies that
    the user is successfully registered and redirected to the login page.
    """
    mock_db.users.find_one.return_value = None  # Simulate no existing user
    response = client_fixture.post(
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

    This test simulates a login request and verifies that
    the user can log in successfully and is redirected appropriately.
    """
    mock_db.users.find_one.return_value = {
        "_id": ObjectId("1234567890abcdef12345678"),
        "username": "test_user",
        "password": generate_password_hash("password"),  # Correctly hashed password
    }

    response = client_fixture.post(
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
    Test the upload audio route.

    This test mocks the file upload process to the '/upload' route,
    processes the audio, and verifies that the file is uploaded and processed successfully.
    """
    mock_user = mock_user_fixture
    upload_folder = "./uploads"
    os.makedirs(upload_folder, exist_ok=True)  # Ensure upload folder exists

    try:
        mock_current_user.get_id.return_value = mock_user.id
        mock_convert.side_effect = lambda input_file, output_file: Path(
            output_file
        ).touch()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        data = {"audio": (io.BytesIO(b"fake audio data"), "fake_audio.wav")}
        response = client_fixture.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        assert response.status_code == 200
        assert b"File uploaded and processed successfully" in response.data
    finally:
        shutil.rmtree(upload_folder)  # Clean up after the test


@patch("app.current_user")
@patch("app.collection")
def test_mood_trends(
    mock_collection, mock_current_user, client_fixture, mock_user_fixture
):
    """
    Test the mood trends API route.

    This test simulates a request to the '/api/mood-trends' route
    and verifies that the correct mood counts are returned.
    """
    mock_user = mock_user_fixture
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.count_documents.side_effect = [
        5,
        3,
        2,
    ]  # Positive, Negative, Neutral counts

    response = client_fixture.get("/api/mood-trends")
    assert response.status_code == 200
    assert response.json == {"Positive": 5, "Negative": 3, "Neutral": 2}


@patch("app.current_user")
@patch("app.collection")
def test_delete_entry(
    mock_collection, mock_current_user, client_fixture, mock_user_fixture
):
    """
    Test deleting a journal entry.

    This test simulates a DELETE request to the '/delete-journal/<id>' route
    and verifies that the journal entry is deleted successfully.
    """
    mock_user = mock_user_fixture
    mock_current_user.get_id.return_value = mock_user.id

    mock_collection.delete_one.return_value.deleted_count = 1

    response = client_fixture.delete("/delete-journal/1234567890abcdef12345678")
    assert response.status_code == 200
    assert b"Entry deleted successfully" in response.data
