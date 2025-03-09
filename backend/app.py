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
CORS(app, resources={r"/infographic": {"origins": "http://localhost:3000"}, r"/change_language": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=['Content-Type'])
app.config['CORS_HEADERS'] = 'Content-Type'

# Loads or retrieves the English spaCy NLP model.
nlp_en = None
def get_nlp_model():
    global nlp_en
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_sm")
    return nlp_en

# Translates text to a specified target language using OpenAI's GPT-4.
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

def wrap_text(text, max_chars_per_line):
    """
    Wraps text at the end of words when length exceeds max_chars_per_line.
    Returns a list of lines.

    Args:
        text (str): The text to wrap
        max_chars_per_line (int): Maximum characters per line

    Returns:
        list: List of text lines
    """
    if not text or len(text) <= max_chars_per_line:
        return [text]

    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        # Check if adding the next word exceeds the max length
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    return lines

# Function to modify SVG for wrapped text
def add_wrapped_text_to_svg(svg_content, element_id, text, max_chars, x_pos, y_pos, font_size=None, font_weight=None, text_anchor=None, direction=None, fill=None):
    """
    Updates SVG content with wrapped text based on character limit

    Args:
        svg_content (str): The SVG content as string
        element_id (str): ID of the text element
        text (str): Text to wrap
        max_chars (int): Maximum characters per line
        x_pos (str/float): X position
        y_pos (str/float): Y position
        font_size (str, optional): Font size with units
        font_weight (str, optional): Font weight
        text_anchor (str, optional): Text anchor
        direction (str, optional): Text direction
        fill (str, optional): Text color

    Returns:
        str: Updated SVG content
    """
    if not text:
        return svg_content

    # Create text element attributes
    attributes = f'id="{element_id}"'
    if font_size:
        attributes += f' font-size="{font_size}"'
    if font_weight:
        attributes += f' font-weight="{font_weight}"'
    if text_anchor:
        attributes += f' text-anchor="{text_anchor}"'
        logging.debug(f"add_wrapped_text_to_svg: element_id={element_id}, text_anchor set to: {text_anchor}") # ENSURE THIS LINE IS PRESENT
    if direction:
        attributes += f' direction="{direction}"'
    if fill:
        attributes += f' fill="{fill}"'

    # Wrap the text
    lines = wrap_text(text, max_chars)

    # Create SVG text element with tspan for each line
    text_element = f'<text font-family="Rubik, sans-serif" {attributes} x="{x_pos}" y="{y_pos}">\n'

    # Calculate line height based on font size (approximately 1.2x font size)
    line_height = 1.2
    if font_size and font_size.endswith('px'):
        try:
            font_size_value = float(font_size.replace('px', ''))
            line_height = font_size_value * 1.2
        except ValueError:
            line_height = 1.2  # Default multiplier if parsing fails

    # Add tspan elements for each line
    for i, line in enumerate(lines):
        dy = "1em" if i == 0 else f"{line_height}px"
        text_element += f'    <tspan x="{x_pos}" dy="{dy}">{line}</tspan>\n'

    text_element += '</text>'

    # Find and replace the existing text element with new wrapped text
    import re
    pattern = f'<text[^>]*id="{element_id}"[^>]*>.*?</text>'
    svg_content = re.sub(pattern, text_element, svg_content, flags=re.DOTALL)

    return svg_content

def shorten_text_gpt(text, target_lang, max_words=7):
    """
    Asks GPT to shorten the given text in the target language to a maximum number of words.

    Args:
        text (str): The text to shorten.
        target_lang (str): The target language.
        max_words (int): Maximum number of words in the shortened text.

    Returns:
        str: Shortened text.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": f"Shorten the following text in {target_lang} to a maximum of {max_words} words, while keeping the original meaning as close as possible:"
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error shortening text with GPT: {e}")
        return text # Return original text in case of error


def create_infographics_for_all(template_file, image_base64, header, sub_header1=None, sub_header2=None, result_prefix="result"):
    languages = {"he": "Hebrew", "en": "English", "ar": "Arabic", "ru": "Russian"}
    footer_texts = {
        "he": "מערך ההסברה של פיקוד העורף",
        "en": "The IDF's Information and Relief Formation",
        "ar": "قسم التوعية في الجبهة الداخلية",
        "ru": "Информационное подразделение Командования тыла",
    }

    # Different character limits for different languages (wrapping limits)
    header_char_limits = {
        "he": 25,
        "en": 25,
        "ar": 30,
        "ru": 25
    }

    subheader_char_limits = {
        "he": 25,
        "en": 25,
        "ar": 25,
        "ru": 20
    }

    # Maximum word counts for header and subheaders
    header_max_words = {
        "he": 10,
        "en": 10,
        "ar": 10,
        "ru": 8
    }

    subheader_max_words = {
        "he": 10,
        "en": 10,
        "ar": 10,
        "ru": 10
    }

    results = {}
    for code, lang in languages.items():
        translated_header = header if code == "he" else translate_text(header, lang)
        translated_sub_header1 = translate_text(sub_header1, lang) if sub_header1 else ""
        translated_sub_header2 = translate_text(sub_header2, lang) if sub_header2 else ""

        header_word_count = len(translated_header.split())
        subheader1_word_count = len(translated_sub_header1.split())
        subheader2_word_count = len(translated_sub_header2.split())

        # Shorten header if it exceeds word limit
        header_max_word_count = header_max_words.get(code, 12)
        if header_word_count > header_max_word_count:
            translated_header = shorten_text_gpt(translated_header, lang, header_max_word_count)

        # Shorten sub_header1 if it exceeds word limit
        subheader1_max_word_count = subheader_max_words.get(code, 9)
        if subheader1_word_count > subheader1_max_word_count:
            translated_sub_header1 = shorten_text_gpt(translated_sub_header1, lang, subheader1_max_word_count)

        # Shorten sub_header2 if it exceeds word limit
        subheader2_max_word_count = subheader_max_words.get(code, 9)
        if subheader2_word_count > subheader2_word_count: # corrected variable name here. It was subheader2_word_count > subheader1_max_word_count
            translated_sub_header2 = shorten_text_gpt(translated_sub_header2, lang, subheader2_max_word_count)

        # Determine text direction and template
        is_rtl = code in ["he", "ar"]
        direction = "rtl" if is_rtl else "ltr"
        text_anchor_rtl = "end"  # For RTL languages
        text_anchor_ltr = "start"    # For LTR languages
        text_anchor = text_anchor_rtl if is_rtl else text_anchor_ltr

        # Choose correct template based on template type and language direction
        actual_template_file = template_file
        if "template2" in template_file and not is_rtl:
            actual_template_file = "template2_ltr.svg"
            logging.info(f"Using LTR template for language: {code}")

        try:
            with open(actual_template_file, "r", encoding="utf-8") as file:
                svg_content = file.read()
                logging.info(f"Successfully opened template file: {actual_template_file}")
        except Exception as e:
            logging.error(f"Error opening template file {actual_template_file}: {e}")
            continue

        # Replace basic placeholders
        # For template 2, direction and text-anchor are hardcoded in the SVG
        if "template2" not in actual_template_file:
            svg_content = svg_content.replace("{{direction}}", direction)
            svg_content = svg_content.replace("{{text_anchor}}", text_anchor)
        svg_content = svg_content.replace("{{footer_text}}", footer_texts[code])

        # Make sure all placeholders are replaced
        if "template2" in actual_template_file:
            # Direct replacement for potential placeholder formats
            svg_content = svg_content.replace("{{sub_header1}}", translated_sub_header1)
            svg_content = svg_content.replace("{{sub_header2}}", translated_sub_header2)

        if image_base64:
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
            # Also try this format of image placeholder
            svg_content = svg_content.replace("BASE64", f"data:image/png;base64,{image_base64}")

        # Apply wrapped text for header and subheaders
        header_limit = header_char_limits.get(code, 25)
        subheader_limit = subheader_char_limits.get(code, 25)

        # Replace header with wrapped version
        svg_content = add_wrapped_text_to_svg(
            svg_content,
            "text1",
            translated_header,
            header_limit,
            "250.0",
            "100.0",
            font_size="32px",
            font_weight="bold",
            text_anchor="middle",  # Header is always centered
            direction=direction,
            fill="#E89024"
        )

        if "template2" in actual_template_file:
            # The x position needs to be adjusted for RTL - try a smaller increment
            subheader_x_pos = "450.0" if is_rtl else "50.0"  # Trying x_pos = 500.0 for RTL
            # subheader_x_pos = "800.0" if is_rtl else "50.0" # OLD - too far right
            # subheader_x_pos = "450.0" if is_rtl else "50.0" # OLD - original value

            if translated_sub_header1:
                svg_content = add_wrapped_text_to_svg(
                    svg_content,
                    "text2",
                    translated_sub_header1,
                    subheader_limit,
                    subheader_x_pos,
                    "250.0",
                    font_size="20px",
                    text_anchor="start", # keep hardcoded value from template2.svg
                    direction=direction, # keep hardcoded value from template2.svg
                    fill="#FFFFFF"
                )

            if translated_sub_header2:
                svg_content = add_wrapped_text_to_svg(
                    svg_content,
                    "text3",
                    translated_sub_header2,
                    subheader_limit,
                    subheader_x_pos,
                    "300.0",
                    font_size="20px",
                    text_anchor="start", # keep hardcoded value from template2.svg
                    direction=direction, # keep hardcoded value from template2.svg
                    fill="#FFFFFF"
                )

        # Log the SVG content for debugging
        logging.debug(f"SVG content for {code}: {svg_content[:500]}...")

        result_file = f"{result_prefix}_{code}.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(svg_content)
            logging.info(f"Successfully wrote SVG to {result_file}")

        results[code] = svg_content

    return results

# Chooses an infographic template based on user input using OpenAI's GPT-4.
def choose_template(user_input_english: str) -> int:
    try:
        template_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Your role is to recieve a prompt from the user that describe an infographic, and you need to choose a template that will display the infographic on the IDF's social media, you can only choose either '1' or '2' (indicates the template you think will best fit to visualize the user input). Template 1 contains a header with up to 10 words, and a big image. Template 2 contains a small header (up to 7 words), an image, and 1-2 sub-headers. You will now recieve the user input and can only choose '1' or '2' based on the template you think will best fit to represent that infographic. The user input - ",
                },
                {"role": "user", "content": user_input_english},
            ],
        )
        template = template_response.choices[0].message.content.strip()
        return template
    except Exception as e:
        logging.error(f"Error choosing template: {e}")
        return 1

# Generates prompts for template 1 infographics using OpenAI's GPT-4.
def generate_prompts1(user_input_english: str) -> tuple:
    try:
        print(f"Generating prompts for user input: {user_input_english}")
        header_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "I'll give you a prompt, and you need to response with an header that should fit the prompt's topic, the header will be displayed on the IDF's social media. "
                    "For example, if the prompt is 'Earthquake', you should generate something like 'How to deal with an earthquake' or 'Earthquake safety tips'. "
                    "Another example is 'Explain about the two steps to defend yourselves from a rocket attack', you should generate something like 'How to defend yourselves from a rocket attack' or 'Instructions during an alarm' or 'Being in public is life-threatening'. "
                    "Another example is 'public transformation' for this you will respond something like 'Instructions for those using public transportation' or 'Public transportation safety'. "
                    "Another example is 'How do you deal with a fire in the house?' for this you will respond something like 'Fire safety tips' or 'Fire prevention'. "
                    "Make sure to not add any details or make up stuff, respond with just a short friendly header in Hebrew (up to 10 words). My prompt is: ",
                },
                {"role": "user", "content": user_input_english},
            ],
        )
        image_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "We'll now play a game where I give you a prompt, and you need to return a prompt describing my prompt. Make sure to not violate OPENAI's TOS, and do not mention peoples religion & race. "
                    "For example, if my prompt is 'Earthquake', you should generate the following prompt 'A man lying on the ground in a park "
                    "Another example is if you get something like 'Explain about the two steps to defend yourselves from a rocket attack', you should generate the following prompt 'A man inside a secure-residential-space (Mamad)', or 'A man lying on the ground in a park "
                    "Another example is 'public transformation' for this you will respond something like 'train on rails in a park' "
                    "Another example is 'How do you deal with a fire in the house?' for this you will respond something like 'Fire in a room' "
                    "Make sure to not add any details or make up stuff, respond with just a short friendly prompt in English. like 'A man lying on the ground in a park'. My prompt is: ",
                },
                {"role": "user", "content": user_input_english},
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
        static_prompt = "Isometric vector illustration in a clean and minimalist, modern style with bright, flat, solid colors and minimal shading, simplified geometric shapes, no background, no text, "
        image_prompt_with_keywords = static_prompt + image_prompt_with_keywords
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

# Generates prompts for template 2 infographics using OpenAI's GPT-4.
def generate_prompts2(user_input_english: str) -> tuple:
    try:
        print(f"Generating prompts for user input: {user_input_english}")
        headers_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a copy generator for infographic posts for the IDF.
                    I want to create an infographic post for the IDF's social media.
                    I have a user input describing the infographic.
                    Generate the following in Hebrew:
                    A header (7 words max).
                    A sub-header (6 words max).
                    An optional second sub-header (6 words max). If no second sub-header is needed, leave this line blank.
                    Please return each item on a new line.
                    User input: """,
                },
                {"role": "user", "content": user_input_english},
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
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "We'll now play a game where I give you a prompt, and you need to return a prompt describing the situation.  Make sure to not violate OPENAI's TOS, and do not mention peoples religion & race. "
                    "For example, if my prompt is 'Earthquake', you should generate the following prompt 'A man lying on the ground in a park "
                    "Another example is if you get something like 'Explain about the two steps to defend yourselves from a rocket attack', you should generate the following prompt 'A man inside a secure-residential-space (Mamad)', or 'A man lying on the ground in a park "
                    "Another example is 'public transformation' for this you will respond something like 'train on rails in a park' "
                    "Another example is 'How do you deal with a fire in the house?' for this you will respond something like 'Fire in a room' "
                    "Make sure to not add any details or make up stuff, respond with just a short friendly prompt in English. like 'A man lying on the ground in a park'. My prompt is: ",
                },
                {"role": "user", "content": user_input_english},
            ],
        )
        image_prompt = image_response.choices[0].message.content.strip()
        print(f"Image prompt generated: {image_prompt}")
        nlp = get_nlp_model()
        doc = nlp(image_prompt)
        keywords = ", ".join([token.text for token in doc if not token.is_stop and token.is_alpha])
        image_prompt_with_keywords = f"{image_prompt}, {keywords}"
        print(f"Image prompt with keywords: {image_prompt_with_keywords}")
        static_prompt = "Isometric vector illustration in a clean and minimalist, modern style with bright, flat, solid colors and minimal shading, simplified geometric shapes, no background, no text, "
        image_prompt_with_keywords = static_prompt + image_prompt_with_keywords

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

# Update the create_infographic1 and create_infographic2 functions to use our text wrapping
def create_infographic1(image_base64, header) -> str:
    """Creates an infographic with template1.svg & the given image and headers."""
    try:
        print(f"Creating infographic with header: {header}, template: 1")
        print(f"Image base64: {image_base64[:100]}...")
        template_file = f"template1.svg"
        with open(template_file, "r", encoding="utf-8") as file:
            svg_content = file.read()
        print(f"SVG content read successfully.")

        # Apply wrapped text for header
        svg_content = add_wrapped_text_to_svg(
            svg_content,
            "text1",
            header,
            25,  # Default character limit
            "250.0",
            "100.0",
            font_size="32px",
            font_weight="bold",
            text_anchor="middle",
            direction="rtl",  # Default to Hebrew
            fill="#E89024"
        )

        if image_base64:
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
            svg_content = svg_content.replace("BASE64", f"data:image/png;base64,{image_base64}")
        print(f"Placeholders replaced successfully.")

        result_file = f"result1.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(svg_content)
        print(f"SVG written to file successfully.")

        return svg_content

    except Exception as e:
        logging.error(f"שגיאה ביצירת אינפוגרפיקה: {e}")
        return None

def create_infographic2(image_base64, header, sub_header1, sub_header2) -> str:
    """Creates an infographic with template2.svg & the given image and headers."""
    try:
        print(f"Creating infographic with header: {header}, template: 2")
        print(f"Image base64: {image_base64[:100]}...")
        
        # For Hebrew (default)
        template_file = "template2.svg"
        direction = "rtl"
        text_anchor = "start"
        
        with open(template_file, "r", encoding="utf-8") as file:
            svg_content = file.read()
        print(f"SVG content read successfully.")

        # Apply wrapped text for headers
        svg_content = add_wrapped_text_to_svg(
            svg_content,
            "text1",
            header,
            25,  # Default character limit
            "250.0",
            "100.0",
            font_size="32px",
            font_weight="bold",
            text_anchor="middle",
            direction=direction,
            fill="#E89024"
        )

        if sub_header1:
            svg_content = add_wrapped_text_to_svg(
                svg_content,
                "text2",
                sub_header1,
                25,  # Shorter character limit for subheaders
                "450.0",
                "250.0",
                font_size="20px",
                text_anchor=text_anchor,
                direction=direction,
                fill="#FFFFFF"
            )

        if sub_header2:
            svg_content = add_wrapped_text_to_svg(
                svg_content,
                "text3",
                sub_header2,
                25,  # Shorter character limit for subheaders
                "450.0",
                "300.0",
                font_size="20px",
                text_anchor=text_anchor,
                direction=direction,
                fill="#FFFFFF"
            )

        if image_base64:
            svg_content = svg_content.replace("{{image}}", f"data:image/png;base64,{image_base64}")
        print(f"Placeholders replaced successfully.")

        result_file = f"result2.svg"
        with open(result_file, "w", encoding="utf-8") as file:
            file.write(svg_content)
        print(f"SVG written to file successfully.")

        return svg_content

    except Exception as e:
        logging.error(f"שגיאה ביצירת אינפוגרפיקה: {e}")
        return None

# Deletes created SVG files after generating a new one.
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
        delete_previous_svgs()  # Delete previous SVGs before generating new ones.
        user_input = request.get_json()['header']
        logging.info(f"User input (Hebrew): {user_input}")

        # Translate user input to English
        user_input_english = translate_text(user_input, "English")
        logging.info(f"User input (English): {user_input_english}")

        template = choose_template(user_input_english)
        if template == '1':
            header, image_base64 = generate_prompts1(user_input_english)
            svg_results = create_infographics_for_all("template1.svg", image_base64, header, result_prefix="result1")
        elif template == '2':
            header, sub_header1, sub_header2, image_base64 = generate_prompts2(user_input_english)
            svg_results = create_infographics_for_all("template2.svg", image_base64, header, sub_header1, sub_header2, result_prefix="result2")
        else:
            logging.error("Invalid template number")
            return jsonify({'error': 'Invalid template number'}), 400
        # Always pass the Hebrew version to the frontend
        return jsonify({'updated_svg': svg_results.get("he")})
    except Exception as e:
        logging.error(f"Error in /infographic endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint to change the language of the displayed infographic.
@app.route('/change_language', methods=['POST'])
def change_language():
    try:
        language = request.get_json()['language']
        # Determine which template was last used by checking for the files.
        template = None
        if os.path.exists("result1_he.svg"):
            template = '1'
            prefix = "result1"
        elif os.path.exists("result2_he.svg"):
            template = '2'
            prefix = "result2"
        else:
            logging.error("No result svg files found")
            return jsonify({'error': 'No result svg files found'}), 500
        # Load the correct svg based on the language.
        file_name = f"{prefix}_{language}.svg"
        with open(file_name, 'r', encoding="utf-8") as f:
            svg_content = f.read()
        return jsonify({'updated_svg': svg_content})
    except Exception as e:
        logging.error(f"Error in /change_language endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Basic route to check if the Flask server is running.
@app.route('/')
def test_route():
    return 'Flask server is running!'

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, port=5000)