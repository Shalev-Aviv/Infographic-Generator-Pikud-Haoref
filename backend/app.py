from flask import Flask, request, jsonify
from flask_cors import CORS #ייבוא ספריית CORS
from googletrans import Translator
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

app = Flask(__name__)
print(STOP_WORDS)
CORS(app)

# טעינת מודל spaCy עבור אנגלית
nlp_en = spacy.load("en_core_web_sm")


@app.route('/infographic', methods=['POST'])
def create_infographic():
    data = request.get_json()
    print('נתונים שהתקבלו:', data) # הוספנו את print()
    text_he = data.get('text')

    translator = Translator()

        # תרגום הטקסט לעברית לאנגלית
    text_en = translator.translate(text_he, dest='en').text

    # ביצוע NLP על הטקסט באנגלית
    doc_en = nlp_en(text_en)
    keywords_en = [token.text for token in doc_en if token.is_alpha and not token.is_stop]

    # יצירת מחרוזת מילות מפתח מופרדות בפסיקים
    keywords_str_en = ", ".join(keywords_en)

    # שילוב הטקסט המקורי ומילות המפתח
    combined_text_en = f"{text_en}, {keywords_str_en}"

    # תרגום הטקסט המשולב לשאר השפות
    translations = {
        'hebrew': f"{text_he}, {', '.join([translator.translate(kw, dest='he').text for kw in keywords_en])}",
        'arabic': translator.translate(combined_text_en, dest='ar').text,
        'russian': translator.translate(combined_text_en, dest='ru').text,
        'english': combined_text_en,
    }

    return jsonify({'translations': translations})

@app.route('/')
def index():
    return "ברוכים הבאים לשרת!"

if __name__ == '__main__':
    app.run(debug=True)
