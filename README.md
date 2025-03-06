# Infographic Generator🎨

## Overview
Infographic Generator is a project aimed at creating personalized infographics automatically. The project features a user-friendly interface where users can input Hebrew text, and receive personalized infographics in various languages. The system uses NLP for keyword extraction, automatic translation, ChatGPT for text generation, and DALL-E3 for image generation.<br>
Stunning infographics in under 30s

## Features✨
- **React-based UI:** An intuitive front-end interface for template selection and text input.
- **Personalized Infographic Creation:** Generating infographics with text and images based on user selection.
- **Multilingual Support:** Support for creating infographics in Hebrew, English, Arabic, and Russian.
- **OPENAI Integration:** Automatic image generation using DALL-E3 based on the input text.
- **NLP Utilization:** Keyword extraction from the text using spaCy to enhance the DALL-E3 prompt.
- **Template Usage:** Utilizing SVG-based templates to create the infographic structure.

## Tech Stack🛠️
- **Frontend**: React 18
- **Backend**: Python 3.10.6, Flask
- **Prompt Generation:** ChatGPT-4 Turbo (OPENAI)
- **Image Generation:** DALL-E3 (OPENAI)
- **NLP:** spaCy
- **Translation:** GoogleTranslator
- **SVG Manipulation:** lxml, svgwrite, cairosvg

## Installation & Usage🚀
### Prerequisites
- Node.js & npm (for the frontend)
- Python 3.10 (for the backend)
- OPENAI_API_KEY (image generator & prompt generator)
### Recommended Versions
- Node 20.12.0
- npm 10.5.0
- Python 3.10.6

### First time running the backend
before running the backend make sure you have the following:
- OPENAI api key with money connected to your account
- created `.env` file inside the backend folder and placed `OPENAI_API_KEY=YOUR_API_KEY`
```sh
cd backend
python3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
### Next time
```sh
cd backend
venv\Scripts\activate
python app.py
```

### First time running the frontend
```sh
cd frontend
npm install
npm install lucide-react
npm start
```
### Next time
```sh
cd frontend
npm start
```

## Contribution🤝
Contributions are welcome! Feel free to submit issues or pull requests.

## License📄
This project is licensed under the MIT License.
