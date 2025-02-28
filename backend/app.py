from flask import Flask, request, jsonify
from flask_cors import CORS #ייבוא ספריית CORS

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

    # כאן תוסיף את הלוגיקה ליצירת האינפוגרפיקה
    # (ניתוח טקסט, תרגום, יצירת פרומפטים, קריאה ל-AI וכו')

    # לצורך הדוגמה, נחזיר תשובה פשוטה
    infographics = {
        'hebrew': 'אינפוגרפיקה בעברית',
        'arabic': 'אינפוגרפיקה בערבית',
        'russian': 'אינפוגרפיקה ברוסית',
        'english': 'אינפוגרפיקה באנגלית'
    }

    return jsonify(infographics)

if __name__ == '__main__':
    app.run(debug=True)