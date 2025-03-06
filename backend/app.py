from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
import spacy
import xml.etree.ElementTree as ET

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, resources={r"/infographic": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=['Content-Type'])
app.config['CORS_HEADERS'] = 'Content-Type'

# Load English NLP model
nlp_en = None
def get_nlp_model():
    global nlp_en
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_sm")
    return nlp_en



def translate_text(text, target_lang):
    if target_lang.lower() == "hebrew":
        return text
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": f"Translate the following text from Hebrew to {target_lang}:"},
                {"role": "user", "content": text}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text

def create_infographics_for_all(template_file, image_base64, header, sub_header1=None, sub_header2=None, result_prefix="result"):
    languages = {"he": "Hebrew", "en": "English", "ar": "Arabic", "ru": "Russian"}
    results = {}
    for code, lang in languages.items():
        translated_header = header if code == "he" else translate_text(header, lang)
        translated_sub_header1 = translate_text(sub_header1, lang) if sub_header1 else ""
        translated_sub_header2 = translate_text(sub_header2, lang) if sub_header2 else ""
        with open(template_file, "r", encoding="utf-8") as file:
            svg_content = file.read()
        svg_content = svg_content.replace("{{header}}", translated_header)
        if sub_header1 is not None:
            svg_content = svg_content.replace("{{sub_header1}}", translated_sub_header1)
            svg_content = svg_content.replace("{{sub_header2}}", translated_sub_header2)
        if image_base64:
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
        result_file = f"{result_prefix}_{code}.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(svg_content)
        results[code] = svg_content
    return results




def choose_template(user_input : str) -> int:
    """בוחר את התבנית המתאימה לפי הקלט של המשתמש."""
    try:
        template_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Your role is to recieve a prompt from the user that describe an infographic, and you need to choose a template that will display the infographic on the IDF's social media, you can only choose either '1' or '2' (indicates the template you think will best fit to visualize the user input). Template 1 contains a header with up to 7 words, and a big image. Template 2 contains a small header (up to 3 words), an image, and 1-2 sub-headers. You will now recieve the user input and can only choose '1' or '2'. The user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )
        template = template_response.choices[0].message.content.strip()
        return template
    except Exception as e:
        logging.error(f"Error choosing template: {e}")
        return 1

def generate_prompts1(user_input: str) -> tuple:
    """Generates prompts for text and image based on the user input."""
    try:
        print(f"Generating prompts for user input: {user_input}")
        header_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a copy generator for infographic posts for the IDF. I want to create an infographic post for the IDF's social media. I have a user input describing the infographic. I need you to extract from there / create a header (6 words max!) that best describes the infographic's topic. Generate the header (6 words max, but keep it as minimal as possible) in Hebrew, for the following user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )

        image_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt generator for infographic posts for the IDF social media social media. I have a user input describing the infographic. Please generate a short prompt in English that will later be used to generate an image for the infographic post. Make sure to NOT include the image style in your prompt because I'll later add that. The user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )

        header = header_response.choices[0].message.content.strip()
        print(f"Header generated: {header}")
        image_prompt = image_response.choices[0].message.content.strip()
        print(f"Image prompt generated: {image_prompt}")

        nlp = get_nlp_model()
        doc = nlp(image_prompt)
        keywords = ", ".join([token.text for token in doc if not token.is_stop and token.is_alpha])
        image_prompt_with_keywords = f"{image_prompt}, {keywords}"
        print(f"Image prompt with keywords: {image_prompt_with_keywords}")

        static_prompt = " Do not include text in the image, color scheme is Brown and green and white, 3D style, minimalistic, clean, no background, no text, no nudity"
        image_prompt_with_keywords = image_prompt_with_keywords + static_prompt

        try:
            dalle_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt_with_keywords,
                n=1,
                size="1024x1024",
                response_format="b64_json",
            )
            image_base64 = dalle_response.data[0].b64_json
            print(f"Image base64 generated: {image_base64[:100]}...")
            return header, image_base64
        except Exception as dalle_error:
            logging.error(f"DALL-E 3 error: {dalle_error}")
            return header, None # return header and None image if error

    except Exception as e:
        logging.error(f"Error generating prompts: {e}")
        return None, None

def generate_prompts2(user_input: str) -> tuple:
    """Generates prompts for text and image based on the user input."""
    try:
        print(f"Generating prompts for user input: {user_input}")
        headers_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a copy generator for infographic posts for the IDF. 
                    I want to create an infographic post for the IDF's social media. 
                    I have a user input describing the infographic. 
                    Generate the following in Hebrew:
                    1. A header (3 words max).
                    2. A sub-header (3 words max).
                    3. An optional second sub-header (3 words max). If no second sub-header is needed, leave this line blank.
                    Please return each item on a new line.
                    User input: """,
                },
                {"role": "user", "content": user_input},
            ],
        )
        headers = headers_response.choices[0].message.content.strip()
        lines = headers.split('\n')
        header = lines[0].strip() if lines else ""
        sub_header1 = lines[1].strip() if len(lines) > 1 else ""
        sub_header2 = lines[2].strip() if len(lines) > 2 else ""
        
        print(f"Header: {header}")
        print(f"Sub-Header 1: {sub_header1}")
        print(f"Sub-Header 2: {sub_header2}")

        image_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt generator for infographic posts for the IDF social media social media. I have a user input describing the infographic. Please generate a short prompt in English that will later be used to generate an image for the infographic post. Make sure to NOT include the image style in your prompt because I'll later add that. The user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )
        image_prompt = image_response.choices[0].message.content.strip()
        print(f"Image prompt generated: {image_prompt}")

        nlp = get_nlp_model()
        doc = nlp(image_prompt)
        keywords = ", ".join([token.text for token in doc if not token.is_stop and token.is_alpha])
        image_prompt_with_keywords = f"{image_prompt}, {keywords}"
        print(f"Image prompt with keywords: {image_prompt_with_keywords}")

        static_prompt = " Do not include text in the image, color scheme is Brown and green and white, 3D style, minimalistic, clean, no background, no text, no nudity"
        image_prompt_with_keywords = image_prompt_with_keywords + static_prompt

        try:
            dalle_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt_with_keywords,
                n=1,
                size="1024x1024",
                response_format="b64_json",
            )
            image_base64 = dalle_response.data[0].b64_json
            print(f"Image base64 generated: {image_base64[:100]}...")
            return header, sub_header1, sub_header2, image_base64
        except Exception as dalle_error:
            logging.error(f"DALL-E 3 error: {dalle_error}")
            return header, None # return header and None image if error

    except Exception as e:
        logging.error(f"Error generating prompts: {e}")
        return None, None

def create_infographic1(image_base64, header) -> str:
    """Creates an infographic with template2.svg & the given image and headers."""
    try:
        print(f"Creating infographic with header: {header}, template: 1")
        print(f"Image base64: {image_base64[:100]}...")  # הדפסה חלקית כדי למנוע הצפת קונסולה
        template_file = f"template1.svg"
        with open(template_file, "r", encoding="utf-8") as file:
            svg_content = file.read()
        print(f"SVG content read successfully.")

        # החלפת מחזיקי המקום
        svg_content = svg_content.replace("{{header}}", header)
        if image_base64 :
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
            svg_content = svg_content.replace("BASE64", f"data:image/png;base64,{image_base64}")
        print(f"Placeholders replaced successfully.")

        root = ET.fromstring(svg_content)
        print(f"XML root created successfully.")

        updated_svg = ET.tostring(root, encoding="unicode")
        print(f"Updated SVG created successfully.")

        result_file = f"result1.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(updated_svg)
        print(f"SVG written to file successfully.")

        return updated_svg

    except Exception as e:
        logging.error(f"שגיאה ביצירת אינפוגרפיקה: {e}")
        return None

def create_infographic2(image_base64, header, sub_header1, sub_header2) -> str:
    """Creates an infographic with template2.svg & the given image and headers."""
    try:
        print(f"Creating infographic with header: {header}, template: 2")  # Corrected template number
        print(f"Image base64: {image_base64[:100]}...")
        template_file = f"template2.svg"  # Corrected template file
        with open(template_file, "r", encoding="utf-8") as file:
            svg_content = file.read()
        print(f"SVG content read successfully.")

        # החלפת מחזיקי המקום
        svg_content = svg_content.replace("{{header}}", header)
        svg_content = svg_content.replace("{{sub_header1}}", sub_header1)
        svg_content = svg_content.replace("{{sub_header2}}", sub_header2)

        if image_base64:
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
        print(f"Placeholders replaced successfully.")

        root = ET.fromstring(svg_content)
        print(f"XML root created successfully.")

        updated_svg = ET.tostring(root, encoding="unicode")
        print(f"Updated SVG created successfully.")

        result_file = f"result2.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(updated_svg)
        print(f"SVG written to file successfully.")

        return updated_svg

    except Exception as e:
        logging.error(f"שגיאה ביצירת אינפוגרפיקה: {e}")
        return None

@app.route('/infographic', methods=['POST'])
def infographic():
    try:
        user_input = request.get_json()['header']
        logging.info(f"User input: {user_input}")
        template = choose_template(user_input)
        if template == '1':
            header, image_base64 = generate_prompts1(user_input)
            svg_results = create_infographics_for_all("template1.svg", image_base64, header, result_prefix="result1")
        elif template == '2':
            header, sub_header1, sub_header2, image_base64 = generate_prompts2(user_input)
            svg_results = create_infographics_for_all("template2.svg", image_base64, header, sub_header1, sub_header2, result_prefix="result2")
        else:
            logging.error("Invalid template number")
            return jsonify({'error': 'Invalid template number'}), 400
        # Always pass the Hebrew version to the frontend
        return jsonify({'updated_svg': svg_results.get("he")})
    except Exception as e:
        logging.error(f"Error in /infographic endpoint: {e}")
        return jsonify({'error': str(e)}), 500




# route בסיסי לבדיקת תקינות
@app.route('/')
def test_route():
    return 'Flask server is running!'



if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, port=5000)