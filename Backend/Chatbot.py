from groq import Groq
from json import loads, dump
import datetime
from dotenv import dotenv_values

#Defining date and time.
current_time=datetime.datetime.now()
Hour=current_time.hour
Minute=current_time.minute
Second=current_time.second

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Load chat history
chat_log_path = r"Data\ChatLog.json"

try:
    with open(chat_log_path, "r") as f:
        messages = loads(f.read())
except (FileNotFoundError, ValueError):
    messages = []
    with open(chat_log_path, "w") as f:
        dump(messages, f)

# System instructions
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname} with real-time internet access.
*** Do not tell time unless asked. Keep responses concise. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Do not provide notes in the output, just answer the question. Never mention your training data. ***
***If the query is asking for current time then give this {Hour} hours {Minute} minutes {Second} seconds***"""

SystemChatBot = [{"role": "system", "content": System}]

# Real-time date and time function
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\nYear: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

# Format chatbot responses
def AnswerModifier(Answer):
    return "\n".join(line for line in Answer.split("\n") if line.strip())

# Chatbot function
def ChatBot(Query):
    global messages
    try:
        messages.append({"role": "user", "content": Query})

        # Generate response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False  # Changed from True to False
        )

        Answer = completion.choices[0].message.content.strip()  # Extract response

        # Store response
        messages.append({"role": "assistant", "content": Answer})

        # Save chat log
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

# Main execution
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(ChatBot(user_input))
