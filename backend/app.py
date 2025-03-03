from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from deep_translator import GoogleTranslator
import spacy
import requests
import logging
import os

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="http://localhost:3000")
app.config['CORS_HEADERS'] = 'Content-Type'

nlp_en = None

def get_nlp_model():
    global nlp_en
    if nlp_en is None:
        nlp_en = spacy.load("en_core_web_sm")
    return nlp_en

def split_first_word(text):
    words = text.split()
    if len(words) > 1:
        return words[0], " ".join(words[1:])
    return words[0], ""

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

    text1_first, text1_rest = split_first_word(text1_en)
    text2_first, text2_rest = split_first_word(text2_en)

    doc_image1 = get_nlp_model()(image1Prompt_en)
    keywords_image1 = [token.text for token in doc_image1 if token.is_alpha and not token.is_stop]
    combined_image1_en = f"{image1Prompt_en}, {', '.join(keywords_image1)}"

    doc_image2 = get_nlp_model()(image2Prompt_en)
    keywords_image2 = [token.text for token in doc_image2 if token.is_alpha and not token.is_stop]
    combined_image2_en = f"{image2Prompt_en}, {', '.join(keywords_image2)}"

    sd_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

    try:
        response = requests.post(sd_url, json={"prompt": combined_image1_en, "steps": 20})
        response.raise_for_status()
        image1_base64 = response.json()["images"][0]
    except Exception as e:
        logging.error(f"Error generating image1: {e}")
        return jsonify({"error": "Stable Diffusion error (image1)"}), 500

    try:
        response = requests.post(sd_url, json={"prompt": combined_image2_en, "steps": 20})
        response.raise_for_status()
        image2_base64 = response.json()["images"][0]
    except Exception as e:
        logging.error(f"Error generating image2: {e}")
        return jsonify({"error": "Stable Diffusion error (image2)"}), 500

    try:
        with open("template.svg", "r") as f:
            template_svg = f.read()
    except Exception as e:
        logging.error(f"Error loading template.svg: {e}")
        return jsonify({"error": "Template SVG not found"}), 500

    updated_svg = template_svg.replace('{{text1_first}}', text1_first)\
                              .replace('{{text1_rest}}', text1_rest)\
                              .replace('{{text2_first}}', text2_first)\
                              .replace('{{text2_rest}}', text2_rest)\
                              .replace('{{image1}}', f"data:image/png;base64,{image1_base64}")\
                              .replace('{{image2}}', f"data:image/png;base64,{image2_base64}")

    response = make_response(updated_svg)
    response.headers['Content-Type'] = 'image/svg+xml'
    return response

@app.route("/")
def helloWorld():
    return "Running Flask server"

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, port=5000)
