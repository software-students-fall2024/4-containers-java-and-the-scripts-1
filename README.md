![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![CI](https://github.com/software-students-fall2024/4-containers-java-and-the-scripts-1/actions/workflows/ci.yml/badge.svg)
# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

![Python build & test](https://github.com/software-students-fall2024/3-python-package-java_and_the_scripts_/actions/workflows/build.yaml/badge.svg)

## Overview
Voice Journal is a hands free, online journal that allows user to create entries by speaking. These entries are transcribed and analyzed to be positive, neutral, or negative in tone in order to provide the user with metrics about their mood over time. 

## Team Members

[Natalie Ovcarov](https://github.com/nataliovcharov)  
[Jun Li](https://github.com/jljune9li)  
[Daniel Brito](https://github.com/danny031103)  
[Alvaro Martinez](https://github.com/AlvaroMartinezM)

## Functions Overview

- **get_audio_files(directory: str) -> list**  
    - **Description**: Retrieves a list of `.wav` audio files from the specified directory.  
    - **Parameters**:  
      - `directory`: The path to the directory containing audio files.  
    - **Returns**: A list of paths to `.wav` audio files.  
    - **Example**:  
      ```python
      get_audio_files("./uploads")
      # Output: ['./uploads/file1.wav', './uploads/file2.wav']
      ```

---

- **transcribe_audio(file_path: str) -> str**  
    - **Description**: Transcribes the audio file at the given path into text.  
    - **Parameters**:  
      - `file_path`: The path to the audio file.  
    - **Returns**: The transcribed text from the audio file. Returns an empty string if transcription fails.  
    - **Example**:  
      ```python
      transcribe_audio("./uploads/audio1.wav")
      # Output: "This is a transcription of the audio file."
      ```

---

- **analyze_sentiment(text: str) -> dict**  
    - **Description**: Analyzes the sentiment of the provided text using TextBlob.  
    - **Parameters**:  
      - `text`: The text to analyze.  
    - **Returns**: A dictionary with keys:  
      - `polarity`: A float (-1 to 1) indicating sentiment polarity.  
      - `subjectivity`: A float (0 to 1) indicating subjectivity.  
      - `mood`: A string ("Positive", "Negative", or "Neutral") based on polarity.  
    - **Example**:  
      ```python
      analyze_sentiment("This is amazing!")
      # Output: {'polarity': 0.9, 'subjectivity': 0.8, 'mood': 'Positive'}
      ```

---

- **store_data(collection, data: dict) -> None**  
    - **Description**: Stores the provided data in the specified MongoDB collection.  
    - **Parameters**:  
      - `collection`: The MongoDB collection where the data will be stored.  
      - `data`: A dictionary containing transcription and sentiment analysis results.  
    - **Returns**: None. Logs a success message when storage is successful.  
    - **Example**:  
      ```python
      data = {
          "user_id": "123",
          "file_name": "audio1.wav",
          "transcript": "This is amazing!",
          "sentiment": {"polarity": 0.9, "subjectivity": 0.8, "mood": "Positive"},
          "timestamp": datetime.utcnow(),
      }
      store_data(collection, data)
      # Output: Logs "Data stored successfully."
      ```

## How to Use This Project
### Platform Configuration
- **Windows** users: Use `python` and `pip` commands instead of `python3` and `pip3` where necessary.
  ```bash
  pip install pipenv
  python your_program_filename.py
  ```


- **macOS/Linux** users: Ensure Python 3 is installed and use `python3`.
  ```bash
  pip3 install pipenv
  python3 your_program_filename.py
  ```

1. **Install `pipenv`** (if not already installed):
    ```bash
    pip3 install pipenv
    ```

2. **Install Dependencies**
    ```bash
    pip3 install -r requirements.txt

    ```

3. **Activate the virtual environment**:
    ```bash
    pipenv shell
    ```

4. **Run the backend functionality**:
    ```bash
    python3 main.py
    ```

5. **Run the Front functionality**:
    ```bash
    python3 app.py
    ```


## How to Run Unit Tests
We've included unit tests for each function in the main.py and utils.py. To run these tests:

1. Install `pytest` in the virtual environment:
    ```bash
    pipenv install pytest
    ```
2. Run the tests from the main project directory:
    ```bash
    python3 -m pytest
    ```
3. Verify all tests pass to ensure correct functionality.

    - **main.py tests**: These tests focus on the backend functionality such as `main()` and `setup_logging()`, ensuring the correct interaction with external systems like MongoDB and file handling.
    
    - **utils.py tests**: These tests cover the utility functions like `get_audio_files()`, `transcribe_audio()`, `analyze_sentiment()`, and `store_data()`, validating tasks like file handling, API interaction, sentiment analysis, and database operations.


## How to Contribute to Project

### Prerequisites
Make sure you have Python 3.9 or higher installed:
```bash
python3 --version
```

1. **Clone the repository**:
    ```bash
    git clone https://github.com/software-students-fall2024/4-containers-java-and-the-scripts-1.git
    ```

2. **Enter the directory**:
    ```bash
    cd 4-containers-java-and-the-scripts-1
    ```

3. **Build the docker containers**
    ```bash
    docker-compose build
    ```

4. **Start the docker containers**
    ```bash
    docker-compose up
    ```

5. **Set up a virtual environment using `pipenv`**:
    ```bash
    pipenv install --dev
    ```

6. **Activate the virtual environment**:
    ```bash
    pipenv shell
    ```

7. **Modify and run the program**:
    ```bash
    python3 machine-learning-client/src/file_name
    ```

   If you want to run a specific file (like `app.py`), use:
    ```bash
    python3 web-app/app.py
    ```

8. **Run tests**:
    ```bash
    pipenv run pytest
    ```

9. **Access the application**
    The application can be used locally at http://localhost:5000.

10. **Shut down the Docker containers**
    ```bash
    docker-compose down
    ```

11. **Exit the virtual environment**:
    ```bash
    exit
    ```

## Notes

This project is meant to be run on Google Chrome, and will not work as intended on other browsers such as Safari. For accurate transcription, please wait 10 seconds between recordings.

## Continuous Integration

This project has a continuous integration workflow that builds and runs unit tests automatically with every push to GitHub.
