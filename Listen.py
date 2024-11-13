import speech_recognition as sr
import numpy as np
import noisereduce as nr
import pyttsx3

# Initialize speech recognizer
recognizer = sr.Recognizer()




# Function of Male voice
def Mtell(text):
    speak = pyttsx3.init() 
    speak.say(text)
    speak.runAndWait()

# Function of Female voice
def Ftell(text):
    engine = pyttsx3.init()
    voice = engine.getProperty("voices")
    engine.setProperty('voice', voice[1].id)
    engine.say(text)
    engine.runAndWait()

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



        return spoken_text

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


continuous_listen()