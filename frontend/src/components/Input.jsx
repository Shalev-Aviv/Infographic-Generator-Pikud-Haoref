import './Input.css';
import React, { useRef, useState, useEffect } from 'react';
import { ImageIcon, Type, Download, Loader } from 'lucide-react';

function Input() {
    const text1Ref = useRef(null);
    const text2Ref = useRef(null);
    const image1PromptRef = useRef(null);
    const image2PromptRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [svgData, setSvgData] = useState(null);
    const [templateSvg, setTemplateSvg] = useState(null);

    useEffect(() => {
        fetch('/template.svg')
            .then(response => response.ok ? response.text() : Promise.reject(`HTTP error! status: ${response.status}`))
            .then(setTemplateSvg)
            .catch(console.error);
    }, []);

    const updateTemplate = () => {
        if (!templateSvg) return '';
        return templateSvg
            .replace(/{{text1}}/g, text1Ref.current?.value || '')
            .replace(/{{text2}}/g, text2Ref.current?.value || '')
            .replace(/{{image1Prompt}}/g, image1PromptRef.current?.value || '')
            .replace(/{{image2Prompt}}/g, image2PromptRef.current?.value || '');
    };

    const handleClick = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:5000/infographic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'image/svg+xml' },
                credentials: 'include',
                body: JSON.stringify({
                    text1: text1Ref.current.value,
                    text2: text2Ref.current.value,
                    image1Prompt: image1PromptRef.current.value,
                    image2Prompt: image2PromptRef.current.value
                }),
            });
            if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
            setSvgData(await response.text());
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
        element.download = "infographic.svg";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    return (
        <div className="infographic-container">
            <div className="infographic-form">
                <div className="input-section">
                    <h2 className="section-title">חלק 1</h2>
                    <div className="input-group">
                        <div className="input-wrapper">
                            <label htmlFor="image1Prompt" className="input-label">
                                <ImageIcon size={18} />
                                <span>תיאור תמונה 1</span>
                            </label>
                            <input 
                                id="image1Prompt"
                                ref={image1PromptRef} 
                                className="input-field" 
                                placeholder="תאר את התמונה שתרצה ליצור..." 
                            />
                        </div>
                        
                        <div className="input-wrapper">
                            <label htmlFor="text1" className="input-label">
                                <Type size={18} />
                                <span>טקסט 1</span>
                            </label>
                            <textarea 
                                id="text1"
                                ref={text1Ref} 
                                className="input-field textarea" 
                                placeholder="הכנס את הטקסט שלך כאן..." 
                                onChange={() => setSvgData(null)} 
                            />
                        </div>
                    </div>
                </div>
                
                <div className="input-section">
                    <h2 className="section-title">חלק 2</h2>
                    <div className="input-group">
                        <div className="input-wrapper">
                            <label htmlFor="image2Prompt" className="input-label">
                                <ImageIcon size={18} />
                                <span>תיאור תמונה 2</span>
                            </label>
                            <input 
                                id="image2Prompt"
                                ref={image2PromptRef} 
                                className="input-field" 
                                placeholder="תאר את התמונה שתרצה ליצור..." 
                            />
                        </div>
                        
                        <div className="input-wrapper">
                            <label htmlFor="text2" className="input-label">
                                <Type size={18} />
                                <span>טקסט 2</span>
                            </label>
                            <textarea 
                                id="text2"
                                ref={text2Ref} 
                                className="input-field textarea" 
                                placeholder="הכנס את הטקסט שלך כאן..." 
                                onChange={() => setSvgData(null)} 
                            />
                        </div>
                    </div>
                </div>
                
                <button 
                    className="generate-button" 
                    onClick={handleClick} 
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <Loader size={18} className="spinner" />
                            <span>מעבד...</span>
                        </>
                    ) : (
                        <span>צור אינפוגרפיקה</span>
                    )}
                </button>
            </div>
            
            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}
            
            <div className="preview-section">
                <h2 className="preview-title">תצוגה מקדימה</h2>
                <div 
                    className="template-preview" 
                    dangerouslySetInnerHTML={{ __html: svgData || updateTemplate() }} 
                />
                
                {svgData && (
                    <button className="download-button" onClick={downloadSvg}>
                        <Download size={18} />
                        <span>הורד SVG</span>
                    </button>
                )}
            </div>
        </div>
    );
}

export default Input;