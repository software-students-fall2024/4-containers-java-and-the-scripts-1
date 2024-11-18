"""
Unit tests for main.py functions, including Flask endpoints and MongoDB operations.
"""

from unittest.mock import patch, MagicMock
from io import BytesIO
import pytest
from src.main import app


@pytest.fixture(name="flask_test_client")
def client_fixture():
    """
    Flask test client fixture for testing Flask endpoints.
    """
    app.testing = True
    with app.test_client() as test_client:
        yield test_client


@patch("src.main.MongoClient")
@patch("src.main.transcribe_audio", return_value="Test transcription")
@patch(
    "src.main.analyze_sentiment",
    return_value={"polarity": 0.5, "subjectivity": 0.6, "mood": "Positive"},
)
def test_process_audio_success(
    mock_analyze_sentiment, mock_transcribe_audio, mock_mongo_client, flask_test_client
):
    """
    Test successful audio processing via `/process-audio`.
    """
    mock_collection = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_collection

    data = {"audio": (BytesIO(b"fake data"), "test.wav")}

    response = flask_test_client.post(
        "/process-audio", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    mock_transcribe_audio.assert_called_once()
    mock_analyze_sentiment.assert_called_once()


@patch("src.main.transcribe_audio", side_effect=RuntimeError("Transcription error"))
def test_process_audio_transcription_error(_mock_transcribe_audio, flask_test_client):
    """
    Test handling of transcription errors during audio processing.
    """
    data = {"audio": (BytesIO(b"fake data"), "test.wav")}

    response = flask_test_client.post(
        "/process-audio", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 500
    assert "Transcription error" in response.json["details"]
