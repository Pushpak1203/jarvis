from googlesearch import search
from groq import Groq
from json import loads, dump
import datetime
from dotenv import dotenv_values

# Load the environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables from the .env file.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the System instructions for the AI chatbot to follow.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = loads(f.read())
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []
except Exception as e:
    print(f"Error loading chat log: {e}")
    messages = []

# Function to perform a google search and format the results.
def GoogleSearch(query: str):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Error during Google search: {e}"

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information about the current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hours = current_date_time.strftime("%H")
    minutes = current_date_time.strftime("%M")
    seconds = current_date_time.strftime("%S")
    data += "Use this Real-Time info if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hours} hours, {minutes} minutes, {seconds} seconds\n"
    return data

# Function to handle real-time search queries.
def RealTimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load previous chat log
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = loads(f.read())
    except FileNotFoundError:
        messages = []
    except Exception as e:
        print(f"Error loading chat log: {e}")
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
    except Exception as e:
        return f"Error during AI model completion: {e}"

    Answer = ""

    # Concatenate the response chunks from the stream.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save the updated chat log.
    try:
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)
    except Exception as e:
        print(f"Error saving chat log: {e}")

    # Remove the most recent system message from the chatbot conversation.
    SystemChatBot.pop()
    return AnswerModifier(Answer)

# Main entry point of the program.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealTimeSearchEngine(prompt))
