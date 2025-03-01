from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import requests
import io
from PIL import Image
import base64

app = Flask(__name__)
CORS(app)

nlp_en = spacy.load("en_core_web_sm")

@app.route('/infographic', methods=['POST'])
def create_infographic():
    data = request.get_json()
    print('נתונים שהתקבלו:', data)
    text_he = data.get('text')

    translator = Translator()
    text_en = translator.translate(text_he, dest='en').text

    doc_en = nlp_en(text_en)
    keywords_en = [token.text for token in doc_en if token.is_alpha and not token.is_stop]
    keywords_str_en = ", ".join(keywords_en)
    combined_text_en = f"{text_en}, {keywords_str_en}"

    translations = {
        'hebrew': f"{text_he}, {', '.join([translator.translate(kw, dest='he').text for kw in keywords_en])}",
        'arabic': translator.translate(combined_text_en, dest='ar').text,
        'russian': translator.translate(combined_text_en, dest='ru').text,
        'english': combined_text_en,
    }

    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"  # התאם את ה-URL ל-API שלך
    payload = {
        "prompt": combined_text_en,
        "steps": 20,  # התאם את מספר הצעדים
    }
    response = requests.post(url, json=payload)

    image_base64 = response.json()["images"][0]
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes))

    image.save("output.png")

    image_base64_str = base64.b64encode(image_bytes).decode('utf-8')

    translations['image'] = image_base64_str

    return jsonify({'translations': translations})

@app.route('/')
def index():
    return "ברוכים הבאים לשרת!"

if __name__ == '__main__':
    app.run(debug=True)