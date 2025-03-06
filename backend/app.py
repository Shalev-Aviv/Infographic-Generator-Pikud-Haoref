from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
import spacy
import xml.etree.ElementTree as ET
import glob

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
#Corrected CORS declaration.
CORS(app, resources={r"/infographic": {"origins": "http://localhost:3000"}, r"/change_language": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=['Content-Type'])
app.config['CORS_HEADERS'] = 'Content-Type'

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

def choose_template(user_input: str) -> int:
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
        static_prompt = " Do not include text in the image, 3D style, minimalistic, clean, no background, no text, no nudity"
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
            return header, None
    except Exception as e:
        logging.error(f"Error generating prompts: {e}")
        return None, None

def generate_prompts2(user_input: str) -> tuple:
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
        headers = headers_response.choices[0].message.content.strip().split('\n')
        header = headers[0]
        sub_header1 = headers[1]
        sub_header2 = headers[2] if len(headers) > 2 else None

        print(f"Header generated: {header}")
        print(f"Sub-header 1 generated: {sub_header1}")
        if sub_header2:
            print(f"Sub-header 2 generated: {sub_header2}")

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
        static_prompt = " Do not include text in the image, 3D style, minimalistic, clean, no background, no text, no nudity"
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
            return header, sub_header1, sub_header2, None
    except Exception as e:
        logging.error(f"Error generating prompts: {e}")
        return None, None, None, None

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

def delete_previous_svgs():
    """Deletes all SVG files with result1_ and result2_ prefixes."""
    for filename in glob.glob("result1_*.svg"):
        try:
            os.remove(filename)
            logging.info(f"Deleted previous SVG: {filename}")
        except OSError as e:
            logging.error(f"Error deleting {filename}: {e}")
    for filename in glob.glob("result2_*.svg"):
        try:
            os.remove(filename)
            logging.info(f"Deleted previous SVG: {filename}")
        except OSError as e:
            logging.error(f"Error deleting {filename}: {e}")

@app.route('/infographic', methods=['POST'])
def infographic():
    try:
        delete_previous_svgs() # Delete previous SVGs before generating new ones.
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


@app.route('/change_language', methods=['POST'])
def change_language():
    try:
        language = request.get_json()['language']

        # Determine which template was last used by checking for the files.
        template = None
        if os.path.exists("result1_he.svg"):
            template = '1'
            file_name = "result1_he.svg"
        elif os.path.exists("result2_he.svg"):
            template = '2'
            file_name = "result2_he.svg"
        else:
            logging.error("No result svg files found")
            return jsonify({'error': 'No result svg files found'}), 500

        if language == "he":
            with open(file_name, 'r', encoding="utf-8") as f:
                svg_content = f.read()
            return jsonify({'updated_svg': svg_content})

        with open(file_name, 'r', encoding="utf-8") as f:
            svg_content = f.read()

        root = ET.fromstring(svg_content)

        if template == '1':
            header_element = root.find(".//{http://www.w3.org/2000/svg}tspan")
            if header_element is not None:
                header_text = header_element.text
                translated_header = translate_text(header_text, language.capitalize())
                header_element.text = translated_header
        elif template == '2':
            header_element = root.find(".//{http://www.w3.org/2000/svg}tspan")
            if header_element is not None:
                header_text = header_element.text
                translated_header = translate_text(header_text, language.capitalize())
                header_element.text = translated_header

            sub_header1_element = root.find(".//{http://www.w3.org/2000/svg}tspan[@id='sub_header1']")
            if sub_header1_element is not None:
                sub_header1_text = sub_header1_element.text
                translated_sub_header1 = translate_text(sub_header1_text, language.capitalize())
                sub_header1_element.text = translated_sub_header1

            sub_header2_element = root.find(".//{http://www.w3.org/2000/svg}tspan[@id='sub_header2']")
            if sub_header2_element is not None:
                sub_header2_text = sub_header2_element.text
                translated_sub_header2 = translate_text(sub_header2_text, language.capitalize())
                sub_header2_element.text = translated_sub_header2

        updated_svg = ET.tostring(root, encoding="unicode")
        return jsonify({'updated_svg': updated_svg})

    except Exception as e:
        logging.error(f"Error in /change_language endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# route בסיסי לבדיקת תקינות
@app.route('/')
def test_route():
    return 'Flask server is running!'

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, port=5000)