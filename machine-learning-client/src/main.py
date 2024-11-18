"""
This module processes audio files, performs transcription and sentiment analysis,
and stores the results in a MongoDB database.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from .utils import transcribe_audio, analyze_sentiment, store_data

load_dotenv()

app = Flask(__name__)


# Set up logging
def setup_logging():
    """
    Set up the logging configuration for the application.

    This function sets the logging level to DEBUG, defines the log format,
    and sets the log handler to stream to the console.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "./processed_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/process-audio", methods=["POST"])
def process_audio():
    """
    Endpoint to process an uploaded audio file and store results in MongoDB.

    Returns:
        JSON: Processed results or error message.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    user_id = request.form.get("user_id")
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)

    try:
        # Save the uploaded file locally
        audio_file.save(file_path)
        logger.info("Saved file: %s", file_path)

        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://root:secret@localhost:27017")
        client = MongoClient(mongo_uri)
        database = client["voice_mood_journal"]
        collection = database["entries"]

        # Perform transcription
        text = transcribe_audio(file_path)
        logger.debug("Transcription: %s", text)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(text)
        logger.debug("Sentiment: %s", sentiment)

        # Prepare data for MongoDB
        data = {
            "user_id": user_id,
            "file_name": audio_file.filename,
            "transcript": text,
            "sentiment": sentiment,
            "timestamp": datetime.utcnow(),
        }

        # Store the data in MongoDB
        store_data(collection, data)
        logger.info("Successfully processed and stored data for %s", file_path)

        return jsonify({"status": "success", "data": data}), 200

    except PyMongoError as mongo_error:
        logger.error("Database error: %s", mongo_error)
        return jsonify({"error": "Database error", "details": str(mongo_error)}), 500

    except RuntimeError as runtime_error:
        logger.error("Runtime error: %s", runtime_error)
        return jsonify({"error": "Runtime error", "details": str(runtime_error)}), 500


def main():
    """
    Main entry point for the application.

    This function prints "Main!" to indicate the program is running.
    """
    print("Main!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
