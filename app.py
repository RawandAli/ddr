from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)

# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CORS(app)

# Initialize the initial messages and prompt
initial_prompt = """"""
gpt_model = "gpt-3.5-turbo"

def initialize_messages():
    return [
        {"role": "system", 
         "content": "Begin first prompt by saying something like 'I will give you a joke and you give me the answer...'. This is your first prompt just introduce yourself and ask the question only, in your first prompt don't ask if I want another joke. Don't give the answer to the joke until I have answered it. And after you give the answer to the joke ask me if I want another one."}
    ]

messages = initialize_messages()
response = client.chat.completions.create(
    model=gpt_model,
    messages=messages
)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response

@app.route('/')
def hello():
    return "Hello, World!"

def add_to_history():
    """Adds newest user input to chat history"""
    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    return response
    
def input_bot(user_input, role="user"):
    """User input to GPT and returns GPT output"""
    messages.append({"role": role, "content": user_input})
    response = add_to_history()
    return response.choices[0].message.content

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
    return jsonify({'response': first_response})

if __name__ == '__main__':
    # Initialize the first response
    messages = initialize_messages()
    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    first_response = response.choices[0].message.content
    input_bot(first_response, role="assistant")
    app.run(debug=True)
