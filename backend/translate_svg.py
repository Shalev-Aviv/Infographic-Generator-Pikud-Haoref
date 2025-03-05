from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

app = Flask(__name__)

def translate_svg(svg_content, target_language='en'):
    """
    מתרגם טקסט בתוך קובץ SVG לשפת היעד.

    :param svg_content: תוכן קובץ ה-SVG כטקסט.
    :param target_language: קוד שפה של שפת היעד (למשל, 'en' לאנגלית, 'ru' לרוסית, 'ar' לערבית).
    :return: תוכן קובץ ה-SVG המתורגם כטקסט.
    """

    try:
        root = ET.fromstring(svg_content)
        translator = GoogleTranslator(source='auto', target=target_language)
        text_elements = root.findall('.//{http://www.w3.org/2000/svg}text')

        for element in text_elements:
            original_text = element.text
            if original_text:
                translated_text = translator.translate(original_text)
                element.text = translated_text

        translated_svg = ET.tostring(root, encoding='unicode')
        return translated_svg

    except Exception as e:
        print(f"שגיאה במהלך תרגום ה-SVG: {e}")
        return None

@app.route('/translate_svg', methods=['POST'])
def translate_svg_endpoint():
    """
    נקודת קצה (endpoint) לתרגום SVG.

    מקבלת בקשת POST עם תוכן SVG ושפת יעד, ומחזירה את ה-SVG המתורגם.
    """
    try:
        data = request.get_json()
        svg_content = data.get('svg_content')
        target_language = data.get('target_language', 'en')  # ברירת מחדל לאנגלית

        if not svg_content:
            return jsonify({'error': 'תוכן SVG חסר'}), 400

        translated_svg = translate_svg(svg_content, target_language)

        if translated_svg:
            return jsonify({'translated_svg': translated_svg})
        else:
            return jsonify({'error': 'שגיאה במהלך תרגום ה-SVG'}), 500

    except Exception as e:
        return jsonify({'error': f'שגיאה: {e}'}), 500
