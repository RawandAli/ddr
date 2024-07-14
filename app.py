from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

# GPT model to be used
gpt_model = "gpt-4o"

def read_knowledge_base(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Initialize knowledge base
knowledge_base_content = read_knowledge_base('doctors.txt')
about_content = read_knowledge_base('about.txt')

prompt = f"""You are a helpful hospital assistant. Answer queries related to our hospital called DDR. \
            Information about our hospital is delimited by triple backticks ```{about_content}```. \
            Information about doctors is delimited by triple apostrophes '''{knowledge_base_content}''' \
            Please read the instructions
            IMPORTANT INSTRUCTIONS: 
            1. Do not provide paragraphs, be short and concise.
            2. Structure your answers in a readtable format.
            3. If the user asks a question about a doctor or a service that is not provided by  us, simply inform them 'We do not provide that service, do you have any other queries?'.
    """
# Function to initialize messages
def initialize_messages():
    return [
        {"role": "system", 
         "content": f"{prompt}"}
    ]
messages = initialize_messages()

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
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages
    )

    # Get the chatbot's response
    bot_response = response.choices[0].message.content
    # Add the bot's response to the message history
    messages.append({"role": "assistant", "content": bot_response})

    return jsonify({'response': bot_response})

@app.route('/first_response', methods=['GET'])
def get_first_response():
    first_response = "Hello, I am your virtual assistant. What would you like help with?"
    messages.append({"role": "assistant", "content": first_response})

    return jsonify({'response': first_response})

if __name__ == '__main__':
    app.run(debug=True)
