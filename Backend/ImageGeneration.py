import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv, get_key
import os
from time import sleep

# Load environment variables from .env file
load_dotenv()

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path=r"Data"
    prompt=prompt.replace(" ","_")

    # Generate the filename for the image
    Files=[f"{prompt}{i}.jpg" for i in range(1,5)]

    for jpg_file in Files:
        image_path=os.path.join(folder_path,jpg_file)

        try:
            # Try to open and display the image
            img=Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Error: Unable to open image: {image_path}")

# API details for Hugging Face Stable diffusion model
API_URL="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers={"Authorization":f"Bearer {os.getenv('HuggingFaceAPIKey')}"}

# Async function to send a query to the Hugging Face API
async def query(payload):
    response=await asyncio.to_thread(requests.post,API_URL,headers=headers,json=payload)
    return response.content

# Function to generate images based on a given prompt
async def generate_images(prompt:str):
    tasks=[]

    # create 4 image generations tasks
    for i in range(4):
        payload={
            "inputs":f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)},"
            }
        task=asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all the tasks to complete
    image_bytes_list=await asyncio.gather(*tasks)

    # Save the generated images to the files
    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ','_')}{i+1}.jpg","wb") as f:
            f.write(image_bytes)

# Wrapper function to generate and open images
def GenerateImages(prompt:str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor for image generation requests
while True:

    try:
        # Read the status and prompt from the data file
        with open(r"Frontend\Files\ImageGeneration.data","r") as f:
            Data:str=f.read()

        Prompt, Status=Data.split(",")

        # If the status indicates an image generation request
        if Status=="True":
            print("Generating images...")
            ImageStatus=GenerateImages(prompt=Prompt)

            # Reset the status in the file after generating the images
            with open(r"Frontend\Files\ImageGeneration.data","w") as f:
                f.write("False, False")
                break

        else:
            sleep(1)

    except:
        pass
 