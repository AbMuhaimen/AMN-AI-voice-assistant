import openai
import json
import os

# open ai api key set up


# File to save conversation history
history_file = 'conversation_history.json'

# Function to load conversation history from file
def load_conversation_history():
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        else:
            return []
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading conversation history: {e}")
        return []

# Function to save conversation history to file
def save_conversation_history(conversation_history):
    try:
        with open(history_file, 'w') as f:
            json.dump(conversation_history, f)
    except IOError as e:
        print(f"Error saving conversation history: {e}")

# Initialize conversation history
conversation_history = load_conversation_history()

def classify_question_with_memory(question):
    try:
        # Add the user question to conversation history
        conversation_history.append({"role": "user", "content": question})
        
        # Define the prompt to classify the question
        prompt = f"Classify the following question into one of these categories: 'general', 'high_definition', 'numerical', 'data_analysis'. Question: {question}"
        
        # Call OpenAI API to classify the question using the new chat API
        response = openai.completions.create(
            model="gpt-3.5-turbo",  # GPT-3.5 model for chat-based completion
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.5
        )
        
        # Get the classification result
        question_type = response['choices'][0]['message']['content'].strip()
        
        # Add classification to the conversation history
        conversation_history.append({"role": "assistant", "content": question_type})
        
        # Save the updated conversation history
        save_conversation_history(conversation_history)
        
        # Return only the classification type (not the answer)
        return question_type
    
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "Error in classifying question"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Unexpected error occurred"

# Test the function with error handling
question1 = "What are the bosson"
print("Question Type:", classify_question_with_memory(question1))

question2 = "Can you explain how quantum computing works?"
print("Question Type:", classify_question_with_memory(question2))

question3 = "How much is 50% of 200?"
print("Question Type:", classify_question_with_memory(question3))

question4 = "Analyze this data for any trends."
print("Question Type:", classify_question_with_memory(question4))




print ("Hello")