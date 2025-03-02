import './Input.css';
import React, { useRef, useState, useEffect } from 'react';

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
            .then((response) => response.text())
            .then((data) => {
                console.log("Template SVG loaded:", data.substring(0, 100));
                setTemplateSvg(data);
            })
            .catch(error => console.error("Error loading template:", error));
    }, []);

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
                    'Accept': 'image/svg+xml',
                },
                credentials: 'include',
                body: JSON.stringify({ text1, text2, image1Prompt, image2Prompt }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const svgText = await response.text();
            setSvgData(svgText);

        } catch (error) {
            console.error('Error:', error);
            setError(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const downloadSvg = () => {
        if (svgData) {
            const element = document.createElement("a");
            const file = new Blob([svgData], { type: 'image/svg+xml' });
            element.href = URL.createObjectURL(file);
            element.download = "infographic.svg";
            document.body.appendChild(element);
            element.click();
        }
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
                <div>
                    <div dangerouslySetInnerHTML={{ __html: svgData }} className="template-preview" />
                    <button onClick={downloadSvg}>הורד SVG</button>
                </div>
            )}
            {!svgData && templateSvg && (
                <div dangerouslySetInnerHTML={{ __html: templateSvg }} className="template-preview" />
            )}
        </div>
    );
}

export default Input;