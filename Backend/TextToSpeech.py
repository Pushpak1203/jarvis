import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Ensure the Data directory exists
os.makedirs("Data", exist_ok=True)

# Asynchronous function to convert text to speech.
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"

    # Remove the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        # Create the communication object to generate speech.
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)  # Ensure saving happens outside the if block
        await asyncio.sleep(1)  # Ensure file is created before proceeding
    except Exception as e:
        print(f"Error generating speech: {e}")

# Function to manage Text-to-Speech (TTS) functionality.
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio asynchronously 
            asyncio.run(TextToAudioFile(Text))

            # Initialize pygame mixer for audio playback.
            pygame.mixer.init()

            # Load the generated speech file into pygame mixer.
            speech_file = r"Data\speech.mp3"
            if not os.path.exists(speech_file):
                print("Error: Speech file not created.")
                return False

            pygame.mixer.music.load(speech_file)
            pygame.mixer.music.play()  # Play the audio file.

            # Loop until the audio is done playing or the function stops.
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)

            return True
        
        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                # Call the provided function with False to signal the end of TTS
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()

            except Exception as e:
                print(f"Error in TTS finally: {e}")

# Function to manage Text-to-Speech with additional responses.
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    # List of predefined responses for cases where text is too long.
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # If the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)

# Main execution block.
if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it to TextToSpeech function.
        TextToSpeech(input("Enter your text: "))
