import spacy
import logging
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load English NLP model
nlp_en = None
def get_nlp_model():
    global nlp_en
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_sm")
    return nlp_en

def generate_prompts(user_input):
    """
    Generates prompts for text and image based on the user input.

    Args:
        user_input (str): The text input from the user.

    Returns:
        tuple: A tuple containing text1, text2, image1_prompt, image2_prompt.
    """
    try:
        header_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a copy generator for infographic posts for the IDF. I want to create an infographic post for the Israeli military's social media. I have a user input describing the infographic. I need you to extract from there / create a header (3 lines at most) that best describes the infographic's topic. Generate the header (3 lines at most, but keep it is minimal as possible) in Hebrew, for the following user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )

        image_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt generator for infographic images that will be a part of an infographic post on the IDF's social media. I have a user input describing the infographic. Please generate a short prompt in English that will later be used to generate an image for the infographic post. Make sure to not include text in the image. Also, please DO NOT mention colors/style in your prompt. The user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )

        header = header_response.choices[0].message["content"].strip()
        image = image_response.choices[0].message["content"].strip()

        return header, image
    except Exception as e:
        logging.error(f"Error generating prompts: {e}")
        return None, None, None #Or raise exception