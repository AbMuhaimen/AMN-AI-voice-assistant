import speech_recognition as sr
import noisereduce as nr
import numpy as np
import pyttsx3 
import openai

# Male and Female voice


# Function of Male voice
def sayf(text):
    speak = pyttsx3.init() 
    speak.say(text)
    speak.runAndWait()

# Function of Female voice
def sayfm(text):
    engine = pyttsx3.init()
    voice = engine.getProperty("voices")
    engine.setProperty('voice', voice[1].id)
    engine.say(text)
    engine.runAndWait()
 
sayfm("Hello, I am AMN!!")
sayf("How can i help you today?")
    
# Function to control noise
def reduce_noise (audio, freq_rate = 16000):
    np_audio = np.frombuffer(audio , dtype=np.int16)                  # Convert to numpy arry
    noise_reduced = nr.reduce_noise(y=np_audio, sr=freq_rate)        # Reduce noise from audio
    return noise_reduced.tobytes()            # Return processed audio
        
        
# Main listen function
def listen():
    print("listening.....")
    recognizer = sr.Recognizer()        # Initalaize Recognizer
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)   # Getting audiio input
    
    try:
        sample_rate = 16000                   # Set sample rate of frequency
        audio_raw = audio.get_raw_data()           # convert to raw data 
        reduced_audio_noise = reduce_noise(audio_raw, sample_rate)        # Reduce noise
        
        
        # Use speech recognition on the noise-reduced audio
        
        spoken_text = recognizer.recognize_google(sr.AudioData(reduced_audio_noise, sample_rate, 2))
        print(f"Recognized text: {spoken_text}")

        return spoken_text
    
    except sr.UnknownValueError:
        sayfm("Sorry, I couldn't understand that.")
        return "Sorry, I couldn't understand that.", None
    except sr.RequestError as e:
        sayf("Sorry, there is a technical error.")
        return f"Error with speech recognition service: {e}", None
    
listen()