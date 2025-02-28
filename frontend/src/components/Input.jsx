import './Input.css';
import React, { useRef } from 'react'; // הוספנו useRef

function Input() {
  const textareaRef = useRef(null); // יצירת ref ל-textarea

  const handleClick = () => {
    const text = textareaRef.current.value; // שימוש ב-ref לקבלת הערך
    console.log('נתונים שנשלחים:', { text: text }); // הוספנו את console.log()

    fetch('http://127.0.0.1:5000/infographic', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('תגובה מהשרת:', data);
        // כאן תוכל לעבד את התגובה מהשרת
      })
      .catch((error) => {
        console.error('שגיאה:', error);
      });
  };

  return (
    <div className="container">
      <textarea
        ref={textareaRef} // חיבור ה-ref ל-textarea
        className="input"
        placeholder="הקלד כאן..."
      ></textarea>
      <button className="submit" onClick={handleClick}>
        שלח
      </button>
    </div>
  );
}

export default Input;