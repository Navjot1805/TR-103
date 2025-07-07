# A beginner-friendly script to generate an image from a text description.
#
# What it does:
# 1. Asks the user for a description of a scene (a "prompt").
# 2. Uses the Hugging Face API to generate an image based on the prompt.
# 3. Displays the generated image to the user.
# 4. Saves the image to a file in the current directory.

# --- Step 1: Install necessary libraries ---
# Before running, open your terminal or command prompt and run these commands:
# pip install requests
# pip install Pillow

# --- Step 2: Import the libraries ---
import requests
import os
from PIL import Image
from io import BytesIO
import re
from datetime import datetime

# --- Step 3: Set up the API information ---
# We'll use a popular Stable Diffusion model from Stability AI via the Hugging Face API.
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# --- Main Functions ---

def get_api_token():
    """
    Prompts the user to enter their Hugging Face API token.
    """
    print("--- Hugging Face API Token ---")
    print("To use this script, you need a free Hugging Face API token.")
    print("1. Go to https://huggingface.co/join to create a free account.")
    print("2. After logging in, go to https://huggingface.co/settings/tokens.")
    print("3. Click 'New token', give it a name (e.g., 'Image Gen'), and choose the 'read' role.")
    print("4. Copy the token and paste it below.")
    
    token = input("Please enter your Hugging Face API token: ")
    return token

def generate_image(api_token, prompt):
    """
    Sends a request to the Hugging Face API to generate an image.
    
    Args:
        api_token (str): The user's Hugging Face API token.
        prompt (str): The text description of the image to generate.
        
    Returns:
        bytes: The raw image data if successful, otherwise None.
    """
    # We must authorize our request with the token
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # The data we send to the API is the prompt
    payload = {"inputs": prompt}
    
    print(f"\n🎨 Generating image for: '{prompt}'")
    print("This may take a moment...")
    
    try:
        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=350) # 120-second timeout
        
        # Check for errors
        if response.status_code != 200:
            error_message = response.json().get("error", "Unknown error")
            print(f"Error: Failed to generate image. Status Code: {response.status_code}")
            print(f"Reason: {error_message}")
            if "currently loading" in error_message:
                print("The model is loading on the server. Please try again in a minute.")
            return None
            
        # If successful, the response content is the image in binary format
        return response.content

    except requests.exceptions.RequestException as e:
        print(f"Error: A network error occurred: {e}")
        return None

def save_and_display_image(image_bytes, prompt):
    """
    Saves the image to a file and tries to display it.
    
    Args:
        image_bytes (bytes): The raw image data.
        prompt (str): The original prompt, used for the filename.
    """
    try:
        # Use Pillow to open the image from the raw bytes
        image = Image.open(BytesIO(image_bytes))
        
        # --- Create a safe filename from the prompt ---
        # 1. Keep only letters, numbers, and spaces
        safe_prompt = re.sub(r'[^\w\s-]', '', prompt).strip()
        # 2. Replace spaces with underscores and make it lowercase
        safe_prompt = re.sub(r'[-\s]+', '_', safe_prompt).lower()
        # 3. Add a timestamp to make it unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 4. Truncate to a reasonable length
        filename = f"{safe_prompt[:50]}_{timestamp}.png"

        # Save the image
        image.save(filename)
        print(f"\n✅ Image successfully saved as: {filename}")
        
        # Display the image
        # This will open the image in your default image viewer.
        # In Google Colab or Jupyter, the image might be displayed inline automatically.
        image.show()

    except Exception as e:
        print(f"Error: Could not save or display the image. {e}")


# --- Main part of the script ---
if __name__ == "__main__":
    api_key = get_api_token()
    
    if not api_key:
        print("API Token is required to run the script. Exiting.")
    else:
        # Get the user's desired scene
        user_prompt = input("\nEnter a description of the image you want to create (e.g., 'A cat wearing a wizard hat'): ")
        
        if not user_prompt:
            print("No prompt provided. Exiting.")
        else:
            # Generate the image
            image_data = generate_image(api_key, user_prompt)
            
            # If we got image data, save and display it
            if image_data:
                save_and_display_image(image_data, user_prompt)
            else:
                print("\nCould not complete the process due to an error.")