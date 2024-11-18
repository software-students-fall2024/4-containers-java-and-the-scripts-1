"""
Unit tests for utility functions in utils.py, including file handling,
transcription, sentiment analysis, and database operations.
"""

from unittest.mock import patch, MagicMock
from speech_recognition import RequestError, UnknownValueError
from src.utils import get_audio_files, transcribe_audio, analyze_sentiment


@patch("src.utils.glob.glob", return_value=["file1.wav", "file2.wav"])
def test_get_audio_files(mock_glob):
    """
    Test the `get_audio_files` function to ensure it returns the correct audio files.
    """
    audio_files = get_audio_files("./mock_directory")
    assert len(audio_files) == 2
    assert "file1.wav" in audio_files
    mock_glob.assert_called_once_with("./mock_directory/*.wav")


@patch("src.utils.sr.Recognizer")
def test_transcribe_audio(mock_recognizer):
    """
    Test the `transcribe_audio` function to ensure it returns the correct transcription.
    """
    mock_instance = MagicMock()
    mock_recognizer.return_value = mock_instance
    mock_instance.record.return_value = "audio data"
    mock_instance.recognize_google.return_value = "Transcription success"

    with patch("src.utils.sr.AudioFile"):
        text = transcribe_audio("mock_file.wav")
        assert text == "Transcription success"
        mock_instance.recognize_google.assert_called_once()


@patch("src.utils.sr.Recognizer")
def test_transcribe_audio_error(mock_recognizer):
    """
    Test the `transcribe_audio` function when a RequestError occurs during transcription.
    """

    # Create a mock Recognizer instance
    mock_instance = MagicMock()
    mock_recognizer.return_value = mock_instance

    # Mock the `record` method to simulate audio data being recorded
    mock_instance.record.return_value = "audio data"

    # Simulate a RequestError being raised during the `recognize_google` call
    mock_instance.recognize_google.side_effect = RequestError("Mocked RequestError")

    # Patch `AudioFile` to avoid actual file I/O
    with patch("src.utils.sr.AudioFile"):
        result = transcribe_audio("mock_file.wav")

    # Ensure the function gracefully handles the exception and returns an empty string
    assert (
        result == ""
    ), "Expected the function to return an empty string on RequestError"


@patch("src.utils.sr.Recognizer")
def test_transcribe_audio_error2(mock_recognizer):
    """
    Test the `transcribe_audio` function when a Unknownerror occurs during transcription.
    """

    # Create a mock Recognizer instance
    mock_instance = MagicMock()
    mock_recognizer.return_value = mock_instance

    # Mock the `record` method to simulate audio data being recorded
    mock_instance.record.return_value = "audio data"

    # Simulate a UnknownError being raised during the `recognize_google` call
    mock_instance.recognize_google.side_effect = UnknownValueError(
        "Mocked Unknown error"
    )

    # Patch `AudioFile` to avoid actual file I/O
    with patch("src.utils.sr.AudioFile"):
        result = transcribe_audio("mock_file.wav")

    # Ensure the function gracefully handles the exception and returns an empty string
    assert (
        result == ""
    ), "Expected the function to return an empty string on UnknownError"


def test_analyze_sentiment():
    """
    Test the `analyze_sentiment` function to ensure it returns correct sentiment analysis.
    """
    result = analyze_sentiment("I love coding")
    assert result["mood"] == "Positive"
    assert result["polarity"] > 0

    result = analyze_sentiment("I hate bugs")
    assert result["mood"] == "Negative"
    assert result["polarity"] < 0
