import speech_recognition as sr
import pyaudio
import wikipedia
import os
import pyttsx3
import openai
import noisereduce as nr
import numpy as np
from scipy.io import wavfile
import json
from mega import Mega
import psutil
import pygetwindow as gw
import keyboard
import time
from datetime import datetime
from transformers import pipeline
from sklearn.ensemble import IsolationForest  # For anomaly detection
import random
import csv


# Function of Male voice
def Mtell(text):
    speak = pyttsx3.init()
    speak.setProperty('rate', 150)  # Adjust speed if needed
    speak.setProperty('volume', 1)  # Set volume level (0.0 to 1.0)
    speak.say(text)
    speak.runAndWait()

# Function of Female voice
def Ftell(text):
    engine = pyttsx3.init()
    voice = engine.getProperty("voices")
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.setProperty('voice', voice[1].id)  # Use second voice (female)
    engine.say(text)
    engine.runAndWait()


# Initialize speech recognizer
recognizer = sr.Recognizer()

# OpenAI API setup


# Function to process audio with noise reduction
def reduce_noise(audio_data, sample_rate=16000):
    # Convert the audio to a numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    # Apply noise reduction
    reduced_noise_audio = nr.reduce_noise(y=audio_np, sr=sample_rate)
    return reduced_noise_audio.tobytes()

# Function to listen, reduce noise, process, and categorize user input
def listen():
    print("Listening... Please speak your command.")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        # Convert audio to numpy array and apply noise reduction
        sample_rate = 16000  # Set the sample rate for noise reduction
        audio_data = audio.get_raw_data()
        reduced_audio_data = reduce_noise(audio_data, sample_rate)

        # Use speech recognition on the noise-reduced audio
        spoken_text = recognizer.recognize_google(sr.AudioData(reduced_audio_data, sample_rate, 2))
        print(f"Recognized text: {spoken_text}")

        # Use OpenAI to classify the intent of the recognized text
        response = openai.Completion.create(
            engine="text-davinci-004",
            prompt=f"Classify the following input into either a 'question', 'open', or 'command' action:\nInput: \"{spoken_text}\"\n\nProvide response category only as 'question', 'open', or 'command'.",
            max_tokens=10
        )

        # Extract and clean up the category response
        category = response['choices'][0]['text'].strip().lower()

        return spoken_text, category

    except sr.UnknownValueError:
        Ftell("Sorry, I couldn't understand that.")
        return "Sorry, I couldn't understand that.", None
    except sr.RequestError as e:
        Mtell("Sorry, there is a technical error.")
        return f"Error with speech recognition service: {e}", None

# Continuous listening loop with "start listening" and "stop listening" feature
def continuous_listen():
    print("Starting continuous listening. Say 'stop listening' to pause or 'start listening' to resume.")
    listening_active = True  # This flag controls whether the assistant is actively listening

    while True:
        if listening_active:
            text, category = listen()
            print(f"Recognized Text: {text}")
            print(f"Category: {category}")

            # Check for stop or start listening commands
            if "stop listening"  or "stop" in text.lower():
                print("Pausing listening. Say 'start listening' to resume.")
                listening_active = False  # Stop listening until "start listening" is said

            elif "start listening" in text.lower():
                print("Already listening.")

        else:
            # Only listen for the "start listening" command when listening is paused
            print("Listening paused. Say 'start listening' to resume.")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            
            try:
                # Recognize the command to start listening again
                spoken_text = recognizer.recognize_google(audio).lower()
                if "start" or "start listening" in spoken_text:
                    print("Resuming listening.")
                    listening_active = True
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                Mtell("Sorry, there is a technical error.")
                print(f"Error with speech recognition service: {e}")

# Initialize MEGA
mega = Mega()
mega_login = mega.login("abdulmuhaimen2080@gmail.com", "AMn@2008")

# Load/Open AI models for assistance
qa_pipeline = pipeline("question-answering")

# Advanced ML model for anomaly detection
anomaly_detector = IsolationForest(n_estimators=100, contamination=0.1)  # Tuned for basic anomaly detection

# Function to monitor and react to system activities
def monitor_system(memory=[]):
    previous_window = None
    cpu_history = []
    memory_history = []

    while True:
        # System stats and anomaly detection
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        current_window = gw.getActiveWindowTitle()

        # Gather data and detect anomalies
        cpu_history.append(cpu_usage)
        memory_history.append(memory_usage)

        # Every 10 readings, train anomaly detection model
        if len(cpu_history) > 10:
            data_points = list(zip(cpu_history, memory_history))
            anomaly_detector.fit(data_points)
            anomalies = anomaly_detector.predict(data_points)
            if -1 in anomalies:
                print("Unusual system activity detected.")

        # Detect specific application usage and take action
        if current_window != previous_window:
            print(f"Active window changed to: {current_window}")
            previous_window = current_window
            if "VS Code" in current_window:
                assistant_response("open_code_editor")
                save_memory_to_mega(memory)  # Log activity to memory

        # Monitor specific keystrokes and initiate advanced response
        if keyboard.is_pressed("ctrl+shift+o"):
            memory.append({"timestamp": datetime.now().isoformat(), "activity": "Command detected"})
            assistant_response("specific_command")
            save_memory_to_mega(memory)  # Log activity to memory

        # Optional delay to reduce CPU load from monitoring
        time.sleep(2)

# Save and load memory with MEGA cloud storage
def save_memory_to_mega(memory, file_name="conversation_memory.json"):
    with open(file_name, "w") as file:
        json.dump(memory, file)
    uploaded_file = mega_login.upload(file_name)
    print("Memory saved to MEGA:", uploaded_file)

def load_memory_from_mega(file_name="conversation_memory.json"):
    files = mega_login.find(file_name)
    if not files:
        print("No previous memory found.")
        return []
    
    file = files[0]
    mega_login.download(file, file_name)
    with open(file_name, "r") as file:
        memory = json.load(file)
        print("Memory loaded from MEGA.")
        return memory

# Assistant response handler
def assistant_response(action):
    print(f"Performing action: {action}")
    
    if action == "open_word":
        os.system("start winword")
        Mtell("Opening Microsoft Word.")
    
    elif action == "create_folder_desktop":
        os.makedirs(os.path.expanduser("~/Desktop/New Folder"), exist_ok=True)
        Ftell("Creating a new folder on your desktop.")
    
    elif action == "delete_file":
        os.remove("project.docx")
        Ftell("Deleting the file named project.docx.")
    
    elif action == "increase_volume":
        os.system("nircmd.exe changesysvolume 5000")  # Example for volume increase using NirCmd
        Mtell("Increasing the volume.")
    
    elif action == "open_vscode":
        os.system("code")
        Mtell("Opening Visual Studio Code.")
    
    elif action == "get_weather_new_york":
        weather = wikipedia.summary("Weather in New York")
        Ftell(weather)
    
    elif action == "search_tech_news":
        news = wikipedia.summary("Latest tech news")
        Ftell(news)
    
    else:
        Ftell("Action not recognized.")


# Seed commands for variation generation
seed_commands = [
    {"command_text": "open Microsoft Word", "action": "open_word"},
    {"command_text": "create a new folder on the desktop", "action": "create_folder_desktop"},
    {"command_text": "delete the file named project.docx", "action": "delete_file"},
    {"command_text": "turn up the volume", "action": "increase_volume"},
    {"command_text": "open VS Code", "action": "open_vscode"},
    {"command_text": "find the weather in New York", "action": "get_weather_new_york"},
    {"command_text": "search Google for the latest tech news", "action": "search_tech_news"},
]

# Generate variations for seed commands using OpenAI
def generate_paraphrases(command_text, num_variations=5):
    paraphrased_variations = []

    prompt = f"Paraphrase the following command into different variations:\n{command_text}\nProvide at least {num_variations} paraphrases."

    for _ in range(num_variations):
        response = openai.Completion.create(
            engine="text-davinci-004",
            prompt=prompt,
            max_tokens=60,
            temperature=0.7
        )
        paraphrased_variation = response['choices'][0]['text'].strip()
        paraphrased_variations.append(paraphrased_variation)
    
    return paraphrased_variations

# Expand seed commands with paraphrases
expanded_commands = []
for command in seed_commands:
    variations = generate_paraphrases(command["command_text"])
    for variation in variations:
        expanded_commands.append({"command_text": variation, "action": command["action"]})

# Save expanded commands into CSV
with open('expanded_command_dataset.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["command_text", "action"])
    for command in expanded_commands:
        writer.writerow([command["command_text"], command["action"]])

# Start continuous listening
continuous_listen()
