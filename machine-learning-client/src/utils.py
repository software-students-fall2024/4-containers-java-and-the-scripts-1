"""
Utility module for handling audio files, performing transcription,
sentiment analysis, and storing data in MongoDB.
"""

import os
import glob
import logging
import speech_recognition as sr
from textblob import TextBlob
from pymongo.errors import PyMongoError


def get_audio_files(directory):
    """
    Retrieves a list of audio files from the specified directory.

    Args:
        directory (str): The path to the directory containing audio files.

    Returns:
        list: A list of paths to audio files.
    """

    audio_files = glob.glob(os.path.join(directory, "*.wav"))
    return audio_files


def transcribe_audio(file_path):
    """
    Transcribes the audio file at the given path to text.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: Transcribed text from the audio.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        logging.error("Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as error:
        logging.error("Could not request results; %s", error)
        return ""


def analyze_sentiment(text):
    """
    Analyzes the sentiment of the provided text using TextBlob.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary with polarity, subjectivity, and mood as keys.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0:
        mood = "Positive"
    elif polarity < 0:
        mood = "Negative"
    else:
        mood = "Neutral"

    sentiment = {"polarity": polarity, "subjectivity": subjectivity, "mood": mood}
    return sentiment


def store_data(collection, data):
    """
    Stores the provided data in the specified MongoDB collection.

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection to store data in.
        data (dict): The data to store.
    """
    try:
        collection.insert_one(data)
        logging.info("Data stored successfully.")
    except PyMongoError as error:
        logging.error("Failed to store data: %s", error)
