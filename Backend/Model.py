import cohere  # Import Cohere library for AI services
from rich import print  # Import the Rich library for better console output
from dotenv import dotenv_values  # Import dotenv to load environment variables from a .env file

# Load the environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve the API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API key
co = cohere.Client(api_key=CohereAPIKey)

# Define recognized function keywords for automation tasks
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble for query classification.
preamble = """You are a very accurate Decision-Making Model that classifies queries into different categories.

*** DO NOT ANSWER QUERIES, ONLY CLASSIFY THEM. ***

-> Respond with 'general ( query )' if a query can be answered by an LLM model (conversational AI chatbot) and doesn't require real-time information.
-> Respond with 'realtime ( query )' if a query requires real-time or up-to-date data, such as:
   - "Who is the current CEO of Tesla?"
   - "What is the weather like today?"
   - "What is today's stock price of Apple?"
   - "Who won the latest football match?"
   - "What time is it now in New York?"
-> Respond with automation tasks like 'open (app)', 'close (app)', 'play (song)', etc., based on user requests.

*** If unsure, classify as 'general ( query )'. ***
"""

# Define chat history with examples for better classification.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "who is Elon Musk?"},
    {"role": "Chatbot", "message": "realtime who is Elon Musk?"},
    {"role": "User", "message": "what is the weather today?"},
    {"role": "Chatbot", "message": "realtime what is the weather today?"},
    {"role": "User", "message": "open chrome and tell me about Mahatma Gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about Mahatma Gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and remind me I have a meeting on 5th Aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th Aug meeting"},
]

# Function to classify the query
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "User", "content": f"{prompt}"})

    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.0,  # Ensure deterministic output
        chat_history=ChatHistory,  # Keep using predefined chat history
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble,
    )

    # Initialize an empty string to store the generated response.
    response = ""

    # Iterate over events in the stream and capture text generation events.
    for event in stream:
        if event.event_type == 'text_generation':
            response += event.text

    # Clean up response
    response = response.replace("\n", "").strip().split(",")

    # Strip leading and trailing whitespaces from each task.
    response = [i.strip() for i in response]

    # Debugging print to check raw response
    print("Raw Response:", response)

    # Initialize an empty list to filter valid tasks.
    temp = []

    # Filter tasks based on recognized function keywords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)

    # If no valid response found, determine classification dynamically
    if not temp:
        # If the query is about real-time topics, classify as "realtime"
        realtime_keywords = ["who is", "today", "now", "current", "latest", "price of", "stock of", "weather", "match score"]
        if any(word in prompt.lower() for word in realtime_keywords):
            return [f"realtime {prompt}"]
        
        # Otherwise, classify as "general"
        return [f"general {prompt}"]

    return temp

# Entry point for the script.
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))
