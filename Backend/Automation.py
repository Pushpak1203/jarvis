# Import all the necessary libraries
from AppOpener import close, open as openApp
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load the environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars["GroqAPIKey"]

# Define CSS classes for passing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses.
professional_responses = [
    "Your satisfaction is my top priority; feel free reach to out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or suport you may need-don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'ContentWriter')}, You're content writer. You have to write content like letter."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    # Nested function to generate content using AI chatbot.
    def ContentWriterAI(Topic):
        messages.append({"role": "user", "content": f"{Topic}"})

        completions = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=False,  # Changed to False for non-streaming
            stop=None
        )

        Answer = completions.choices[0].message.content  # Access content directly

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})  # Use the actual answer
        return Answer

    Topic = Topic.replace("Content", "").strip()  # Remove "Content" and strip whitespace
    ContentByAI = ContentWriterAI(Topic)

    # Save the generated content to a text file.
    filename = f"Data{Topic.lower().replace(' ', '')}.txt"
    filepath = os.path.join("Data", filename)  # Construct the full file path
    os.makedirs("Data", exist_ok=True)  # Ensure the "Data" directory exists

    with open(filepath, 'w', encoding='utf-8') as file:  # Use 'w' mode to overwrite
        file.write(ContentByAI)
        file.close()

    OpenNotepad(filepath)
    return True

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query)
    return True

# Function to open an application or relevant webpages.
def OpenApp(app, sess=requests.session()):
    try:
        openApp(app, match_closest=True, output=True, throw_error=True)  # Corrected function call
        return True

    except Exception as e:
        print(f"Error opening app using AppOpener: {e}")

        # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        # Nested function to perform a Google search and retrieve HTML.
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
            return None

        html = search_google(app)

        if html:
            link = extract_links(html)[0]
            webopen(link)

        return True

# Function to close an application.
def CloseApp(app):
    if "chrome" in app:
        return True  # Do nothing for Chrome
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception as e:
            print(f"Error closing app: {e}")
            return False

# Function to execute system-level commands.
def System(command):

    # Nested function to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute")

    # Nested function to unmute the system volume.
    def unmute():
        keyboard.press_and_release("volume mute")

    # Nested function to increase the system volume.
    def volume_up():
        keyboard.press_and_release("volume up")

    # Nested function to decrease the system volume.
    def volume_down():
        keyboard.press_and_release("volume down")

    # Execute the appropriate system command.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        command = command.lower()  # Normalize commands to lowercase

        if command.startswith("open"):
            app_name = command.removeprefix("open").strip()
            if app_name not in ["it", "file"]:
                fun = asyncio.to_thread(OpenApp, app_name)
                funcs.append(fun)

        elif command.startswith("close"):
            app_name = command.removeprefix("close").strip()
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)

        elif command.startswith("play"):
            query = command.removeprefix("play").strip()
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)

        elif command.startswith("content"):
            topic = command.removeprefix("content").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)

        elif command.startswith("google search"):
            topic = command.removeprefix("google search").strip()
            fun = asyncio.to_thread(GoogleSearch, topic)
            funcs.append(fun)

        elif command.startswith("youtube search"):
            topic = command.removeprefix("youtube search").strip()
            fun = asyncio.to_thread(YouTubeSearch, topic)
            funcs.append(fun)

        elif command.startswith("system"):
            system_command = command.removeprefix("system").strip()
            fun = asyncio.to_thread(System, system_command)
            funcs.append(fun)

        else:
            print(f"Unknown command: {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return


