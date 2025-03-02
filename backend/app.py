from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from deep_translator import GoogleTranslator
import spacy
import requests
import io
from PIL import Image
import base64
import svg_template
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)  # הגדרת רמת ה-logging ל-DEBUG

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="http://localhost:3000")
app.config['CORS_HEADERS'] = 'Content-Type'

nlp_en = None

def get_nlp_model():
    global nlp_en
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_sm")
    return nlp_en

@app.route('/infographic', methods=['POST'])
def create_infographic():
    logging.debug("Received POST request at /infographic")
    
    data = request.get_json()
    text1 = data.get('text1')
    text2 = data.get('text2')
    image1Prompt = data.get('image1Prompt')
    image2Prompt = data.get('image2Prompt')

    text1_en = GoogleTranslator(source='auto', target='en').translate(text1)
    text2_en = GoogleTranslator(source='auto', target='en').translate(text2)
    image1Prompt_en = GoogleTranslator(source='auto', target='en').translate(image1Prompt)
    image2Prompt_en = GoogleTranslator(source='auto', target='en').translate(image2Prompt)

    # חילוץ מילות מפתח עבור כל תמונה
    doc_image1 = get_nlp_model()(image1Prompt_en)
    keywords_image1 = [token.text for token in doc_image1 if token.is_alpha and not token.is_stop]
    doc_image1 = get_nlp_model()(image1Prompt_en)
    keywords_str_image1 = ", ".join(keywords_image1)
    combined_image1_en = f"{image1Prompt_en}, {keywords_str_image1}"

    doc_image2 = get_nlp_model()(image2Prompt_en)
    keywords_image2 = [token.text for token in doc_image2 if token.is_alpha and not token.is_stop]
    keywords_str_image2 = ", ".join(keywords_image2)
    combined_image2_en = f"{image2Prompt_en}, {keywords_str_image2}"

    # קוד Stable Diffusion עבור תמונה 1
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"  # התאם ל-URL שלך
    payload = {
        "prompt": combined_image1_en,
        "steps": 20,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response_json = response.json()
        logging.debug(f"Stable Diffusion API response (image1): {json.dumps(response_json)}")
        image1_base64 = response_json["images"][0]
        # image1_bytes = base64.b64decode(image1_base64)
        # image1 = Image.open(io.BytesIO(image1_bytes))
        # image1.save("image1.png")
    except requests.exceptions.RequestException as e:
        logging.error(f"Stable Diffusion request failed (image1): {e}")
        return jsonify({"error": "Stable Diffusion error (image1)"}), 500
    except KeyError:
        logging.error("Stable Diffusion API response missing 'images' key (image1)")
        return jsonify({"error": "Stable Diffusion API error (image1)"}), 500
    except Exception as e:
        logging.error(f"An error occurred (image1): {e}")
        return jsonify({"error": "Internal server error (image1)"}), 500

    # קוד Stable Diffusion עבור תמונה 2
    payload = {
        "prompt": combined_image2_en,
        "steps": 20,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_json = response.json()
        logging.debug(f"Stable Diffusion API response (image2): {json.dumps(response_json)}")
        image2_base64 = response_json["images"][0]
        # image2_bytes = base64.b64decode(image2_base64)
        # image2 = Image.open(io.BytesIO(image2_bytes))
        # image2.save("image2.png")
    except requests.exceptions.RequestException as e:
        logging.error(f"Stable Diffusion request failed (image2): {e}")
        return jsonify({"error": "Stable Diffusion error (image2)"}), 500
    except KeyError:
        logging.error("Stable Diffusion API response missing 'images' key (image2)")
        return jsonify({"error": "Stable Diffusion API error (image2)"}), 500
    except Exception as e:
        logging.error(f"An error occurred (image2): {e}")
        return jsonify({"error": "Internal server error (image2)"}), 500

    # יצירת SVG
    try:
        # svg_template.create_svg_template("output.svg")
        # svg_template.insert_text_into_svg("output.svg", text1_en, "text1")
        # svg_template.insert_text_into_svg("output.svg", text2_en, "text2")
        # svg_template.insert_image_into_svg("output.svg", "image1.png", "image1")
        # svg_template.insert_image_into_svg("output.svg", "image2.png", "image2")

        # החזרת ה-SVG ל-frontend
        return jsonify({
            "text1": text1_en,
            "text2": text2_en,
            "image1": image1_base64,
            "image2": image2_base64
        })
    except Exception as e:
        logging.error(f"Error creating SVG: {e}")
        return jsonify({"error": "Error creating SVG"}), 500

@app.route("/")
def helloWorld():
    return "Hello, World!"

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, port=5000)