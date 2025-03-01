from flask import Flask, request, jsonify
from flask_cors import CORS #ייבוא ספריית CORS
from googletrans import Translator

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "ברוכים הבאים לשרת!"

@app.route('/infographic', methods=['POST'])
def create_infographic():
    data = request.get_json()
    print('נתונים שהתקבלו:', data) # הוספנו את print()
    text = data.get('text')

    translator = Translator()

    # כאן תוסיף את הלוגיקה ליצירת האינפוגרפיקה
    # (ניתוח טקסט, תרגום, יצירת פרומפטים, קריאה ל-AI וכו')

    # תרגום לארבע שפות
    translations = {
        'hebrew': text,
        'arabic': translator.translate(text, dest='ar').text,
        'russian': translator.translate(text, dest='ru').text,
        'english': translator.translate(text, dest='en').text,
    }

    return jsonify(translations)

if __name__ == '__main__':
    app.run(debug=True)