import './Input.css';
import React, { useRef, useState } from 'react'; // הוספנו useState

function Input() {
  const textareaRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null); // הוספנו state לתמונה

  const handleClick = () => {
    const text = textareaRef.current.value;
    console.log('נתונים שנשלחים:', { text: text });

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
        if (data.translations && data.translations.image) {
          setImageSrc(`data:image/png;base64,${data.translations.image}`); // הגדרת state לתמונה
        } else {
          console.error('התמונה לא נמצאה בתגובה מהשרת.');
        }
      })
      .catch((error) => {
        console.error('שגיאה:', error);
      });
  };

  return (
    <div className="container">
      <textarea
        ref={textareaRef}
        className="input"
        placeholder="הקלד כאן..."
      ></textarea>
      <button className="submit" onClick={handleClick}>
        שלח
      </button>
      {imageSrc && <img src={imageSrc} alt="Infographic" />} {/* הצגת התמונה */}
    </div>
  );
}

export default Input;