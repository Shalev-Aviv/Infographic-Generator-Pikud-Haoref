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

def generate_prompts(user_input):
    """Generates prompts for text and image based on the user input."""
    try:
        print(f"Generating prompts for user input: {user_input}")
        header_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a copy generator for infographic posts for the IDF. I want to create an infographic post for the Israeli military's social media. I have a user input describing the infographic. I need you to extract from there / create a header (3 lines at most) that best describes the infographic's topic. Generate the header (3 lines at most, but keep it is minimal as possible) in Hebrew, for the following user input - ",
                },
                {"role": "user", "content": user_input},
            ],
        )

        image_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt generator for infographic images that will be a part of an infographic post on the IDF's social media. I have a user input describing the infographic. Please generate a short prompt in English that will later be used to generate an image for the infographic post. Make sure to not include text in the image. Also, please add to the prompt the following things so every image will look the same style - Brown, green, and white color scheme, low-poly 3D style, minimalistic, clean, no background. The user input - ",
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

        try:
            dalle_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt_with_keywords,
                n=1,
                size="1024x1024",  # גודל תמונה נתמך
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

def create_infographic(image_base64, header, template_num=1):
    """יוצר SVG חדש בשם result{template_num}.svg עם התמונה והכותרת החדשות ומחזיר אותו לצד הלקוח."""
    try:
        print(f"Creating infographic with header: {header}, template: {template_num}")
        print(f"Image base64: {image_base64[:100]}...")  # הדפסה חלקית כדי למנוע הצפת קונסולה
        template_file = f"template{template_num}.svg"
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

        result_file = f"result{template_num}.svg"
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
        header, image_base64 = generate_prompts(user_input)
        logging.info(f"Header: {header}, Image base64: {image_base64[:100]}...")
        updated_svg = create_infographic(image_base64, header)
        logging.info(f"Updated SVG: {updated_svg}")
        return jsonify({'updated_svg': updated_svg})
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