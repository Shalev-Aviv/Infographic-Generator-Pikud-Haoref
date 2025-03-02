import './Input.css';
import React, { useRef, useState } from 'react';

function Input() {
    const text1Ref = useRef(null);
    const text2Ref = useRef(null);
    const image1PromptRef = useRef(null);
    const image2PromptRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [svgData, setSvgData] = useState(null); // הוספת state עבור נתוני ה-SVG

    const handleClick = async () => {
        setLoading(true);
        setError(null);

        try {
            const text1 = text1Ref.current.value;
            const text2 = text2Ref.current.value;
            const image1Prompt = image1PromptRef.current.value;
            const image2Prompt = image2PromptRef.current.value;

            console.log('Sending data:', { text1, text2, image1Prompt, image2Prompt });

            const response = await fetch('http://127.0.0.1:5000/infographic', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json', // שינוי ל-application/json
                },
                credentials: 'include',
                body: JSON.stringify({ text1, text2, image1Prompt, image2Prompt }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json(); // קבלת נתוני JSON מהשרת
            console.log('Received data:', data);

            // עדכון ה-PLACEHOLDERS ב-SVG
            const updatedSvg = updateSvgPlaceholders(data);
            setSvgData(updatedSvg);

        } catch (error) {
            console.error('Error:', error);
            setError(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const updateSvgPlaceholders = (data) => {
        // כאן תוסיף את הלוגיקה לעדכון ה-PLACEHOLDERS ב-SVG
        // לדוגמה, תוכל להשתמש ב-DOMParser כדי לטעון את ה-SVG,
        // למצוא את האלמנטים המתאימים ולעדכן את התוכן שלהם.
        // אם ה-SVG שלך מורכב, ייתכן שתצטרך להשתמש בספרייה כמו 'svg-parser'.
        // לעת עתה, נחזיר מחרוזת SVG פשוטה עם הנתונים שהתקבלו.
        return `
            <svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
                <text x="50" y="50">${data.text1}</text>
                <text x="50" y="100">${data.text2}</text>
                <image x="50" y="150" width="200" height="150" href="data:image/png;base64,${data.image1}" />
                <image x="50" y="300" width="200" height="150" href="data:image/png;base64,${data.image2}" />
            </svg>
        `;
    };

    return (
        <div className="container">
            <div className="input-group">
                <input ref={image1PromptRef} className="input" placeholder="תמונה 1" />
                <textarea ref={text1Ref} className="input" placeholder="טקסט 1" />
            </div>
            <div className="input-group">
                <input ref={image2PromptRef} className="input" placeholder="תמונה 2" />
                <textarea ref={text2Ref} className="input" placeholder="טקסט 2" />
            </div>
            <button
                className="submit"
                onClick={handleClick}
                disabled={loading}
            >
                {loading ? 'מעבד...' : 'צור אינפוגרפיקה'}
            </button>
            {error && <div className="error">{error}</div>}
            {svgData && (
                <div dangerouslySetInnerHTML={{ __html: svgData }} className="template-preview" />
            )}
        </div>
    );
}

export default Input;