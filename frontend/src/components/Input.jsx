import './Input.css';
import React, { useRef, useState, useEffect } from 'react';
import { Download, Loader } from 'lucide-react';

function Input() {
    const serverUrl = `http://127.0.0.1:${process.env.REACT_APP_SERVER_PORT || 5000}`;
    const infographicData = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [svgData, setSvgData] = useState(null);
    const previewRef = useRef(null);
    const [isLanguagePopupOpen, setIsLanguagePopupOpen] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('he');
    const [svgLoaded, setSvgLoaded] = useState(false);

    const handleClick = async () => {
        console.log("handleClick called");
        console.log("Input value:", infographicData.current.value);
        setError(null);
        setLoading(true);
        try {
            console.log("Sending request with data:", infographicData.current.value);
            const response = await fetch(`${serverUrl}/infographic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    header: infographicData.current.value,
                }),
            });
            console.log("Response received:", response);
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Data received:", data);
            setSvgData(data.updated_svg);
            setSvgLoaded(true);
        } catch (error) {
            console.error('Error:', error);
            setError(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const downloadSvg = () => {
        if (!svgData) return;
        const element = document.createElement("a");
        element.href = URL.createObjectURL(new Blob([svgData], { type: 'image/svg+xml' }));
        element.download = `infographic_${selectedLanguage}.svg`; // Use selectedLanguage here
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    useEffect(() => {
        if (svgData && previewRef.current) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(svgData, 'image/svg+xml');
            const svgElement = doc.documentElement;
            previewRef.current.innerHTML = '';
            previewRef.current.appendChild(svgElement);
        }
    }, [svgData]);

    useEffect(() => {
        if (!svgData && previewRef.current) {
            previewRef.current.innerHTML = '';
        }
    }, [svgData]);

    const changeLanguage = () => {
        setIsLanguagePopupOpen(true);
    };

    const [tempSelectedLanguage, setTempSelectedLanguage] = useState('he'); // New state

    const handleLanguageSelection = (language) => {
        setTempSelectedLanguage(language);
    };

    const confirmLanguageSelection = async () => {
        setSelectedLanguage(tempSelectedLanguage);
        setIsLanguagePopupOpen(false);
        setLoading(true);
        try {
            const response = await fetch(`${serverUrl}/change_language`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: tempSelectedLanguage }),
            });
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            const data = await response.json();
            setSvgData(data.updated_svg);
        } catch (error) {
            console.error('Error:', error);
            setError(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="infographic-container">
            <div className="infographic-form">
                <div className="input-section">
                    <h2 className="section-title">יצירת אינפוגרפיקה</h2>
                    <div className="input-group">
                        <div className="input-wrapper">
                            <textarea id="header" ref={infographicData} className="input-field textarea" placeholder="תאר את האינפוגרפיה שתרצה ליצור" onChange={() => setSvgData(null)} />
                        </div>
                    </div>
                    <button className="generate-button" onClick={handleClick} disabled={loading} >
                        {loading ? (<><Loader size={18} className="spinner" /><span>מעבד...</span></>) : (<span>צור אינפוגרפיקה</span>)}
                    </button>
                </div>
            </div>
            {error && (<div className="error-message"><p>{error}</p></div>)}
            <div className="preview-section">
                <h2 className="preview-title">תוצר סופי</h2>
                <div className="template-preview" ref={previewRef} onClick={svgLoaded ? changeLanguage : null} />
                {svgData && (<button className="download-button" onClick={downloadSvg}><Download size={18} /><span>הורד SVG</span></button>)}
            </div>
            {isLanguagePopupOpen && (
            <div className="background-dim">
                <div className="language-popup">
                    <h2 className="popup-title">בחירת שפה</h2>
                    <select value={tempSelectedLanguage} className="language-select" onChange={(e) => handleLanguageSelection(e.target.value)}>
                        <option value="he">עברית</option>
                        <option value="ar">ערבית</option>
                        <option value="en">אנגלית</option>
                        <option value="ru">רוסית</option>
                    </select>
                    <div className="button-container">
                        <button className="cancel-button" onClick={() => setIsLanguagePopupOpen(false)}>ביטול</button>
                        <button className="confirm-button" onClick={confirmLanguageSelection}>אישור</button> {/* Call the new function */}
                    </div>
                </div>
            </div>
        )}
        </div>
    );
}

export default Input;