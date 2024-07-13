from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from openai import OpenAI
import os

app = Flask(__name__)

# Configure the session to use filesystem (or you can configure it to use Redis, etc.)
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in the filesystem
app.secret_key = 'super secret key'  # Secret key for signing cookies
Session(app)  # Initialize the session extension

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CORS(app)

# GPT model to be used
gpt_model = "gpt-3.5-turbo"

# Function to initialize messages
def initialize_messages():
    return [
        {"role": "system", 
         "content": "Begin first prompt by saying something like 'I will give you a joke and you give me the answer...'. This is your first prompt just introduce yourself and ask the question only, in your first prompt don't ask if I want another joke. Don't give the answer to the joke until I have answered it. And after you give the answer to the joke ask me if I want another one."}
    ]

# Function to add to history and get response from OpenAI
def add_to_history(user_messages):
    response = client.chat.completions.create(
        model=gpt_model,
        messages=user_messages
    )
    return response

# Function to process user input and get bot response
def input_bot(user_input, role="user"):
    if 'messages' not in session:
        session['messages'] = initialize_messages()
    user_messages = session['messages']
    user_messages.append({"role": role, "content": user_input})
    response = add_to_history(user_messages)
    session['messages'] = user_messages
    if role == "user":
        return response.choices[0].message.content

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    # Get the chatbot's response
    bot_response = input_bot(f"'''{user_message}'''")
    # Add the bot's response to the message history
    input_bot(bot_response, role="assistant")
    
    return jsonify({'response': bot_response})

@app.route('/first_response', methods=['GET'])
def get_first_response():
    response = client.chat.completions.create(
        model=gpt_model,
        messages=session['messages']
    )
    first_response = response.choices[0].message.content
    input_bot(first_response, role="assistant")
    return jsonify({'response': first_response})

if __name__ == '__main__':
    app.run(debug=True)
