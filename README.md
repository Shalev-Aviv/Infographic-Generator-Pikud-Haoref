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

## Time⌛
- Generates the final SVG in under 1min
## Cost💸
- Costs $0.05-$0.08 for a set of 4 infographics (depends on the chosen template and input length)

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
- created `.env` file inside the backend folder with the following:
`OPENAI_API_KEY=YOUR_API_KEY`
`SERVER_PORT=YOUR_BACKEND_PORT`
`CLIENT_PORT=YOUR_FRONTEND_PORT`
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
before running the backend make sure you have the following:
- created `.env` file inside the frontend folder with the following:
`REACT_APP_SERVER_PORT=YOUR_BACKEND_PORT`
```sh
cd frontend
npm install
npm install lucide-react
npm start

### Next time
```sh
cd frontend
npm start

```# Infographic Generator Project - Version 1.1.1🚀

## Description:
Version 1.1.2 of the Infographic Generator is now live!🥳 Building upon the improvements of version 1.1.1, this update focuses on refining the infographic generation process through minor prompt engineering enhancements and fixes for SVG text rendering. These changes contribute to more accurate and visually appealing multilingual infographics. Continue to leverage this powerful Flask and Python backend service for all your infographic needs! 🎨🖼️

## Key Features:
- **Language-Specific Download Filenames:** Downloaded SVG files are now named with their language codes (e.g., `infographic_he.svg`, `infographic_en.svg`), making file management a breeze.
- **AI-Powered Template Selection:** Utilizes OpenAI's GPT-4 to analyze user input text and intelligently choose between two infographic templates (`template1.svg` and `template2.svg`). Template 1 is designed for a large header and a prominent image, while Template 2 offers a smaller header, an image, and optional sub-headers.
- **Multilingual Content Generation:** Generates infographic content in multiple languages, including Hebrew (the base language), English, Arabic, and Russian. GPT-4 translates header and sub-header text from Hebrew to the target languages.
- **Dynamic Text Creation:** Leverages GPT-4 to generate relevant and concise header and subheader text in Hebrew based on the user's input prompt. It also includes text shortening and wrapping functionalities to ensure text fits within the infographic templates, considering character and word limits specific to each language.
- **Automated Image Generation:** It integrates with DALL-E 3, OpenAI's image-generation model, to create visually relevant images for the infographics. Prompts for image generation are dynamically created based on the user's input and enhanced with keywords for better image quality.
- **SVG Template-Based Infographics:** Utilizes pre-designed SVG (Scalable Vector Graphics) templates to structure the infographics. The project currently supports two templates, each offering a different layout and text element arrangement.
- **RTL & LTR Language Harmony!** 🤝🌍 Language direction? No problem! Masterfully handles both RTL (Hebrew, Arabic) and LTR (English, Russian).

## Tech Stack - Built to Impress! 💪🐍
- **Flask:** A Python web framework for creating the backend API.
- **OpenAI API (GPT-4, DALL-E 3):** For text generation, translation, template selection, and image generation.
- **spaCy:** For natural language processing tasks, specifically keyword extraction from prompts.
- **SVG (Scalable Vector Graphics):** For the infographic templates and output format.
- **dotenv:** For managing environment variables (API keys).
- **Python XML libraries:** For working with SVG file content.

## **REST API Powerhouse!** 💻🔌
Two robust API endpoints at your service:
- `/infographic` (POST): Generate multilingual SVG infographic files on demand! Returns the Hebrew SVG masterpiece to your frontend.
- `/change_language` (POST): Effortlessly switch language versions and get the perfect SVG content.

# Changes in Version 1.1.2:
**IMPROVED!** Enhanced infographic generation through minor prompt engineering adjustments.
**FIXED!** Addressed issues related to SVG text rendering for improved visual output.

## Limitations in Version 1.1.2 (Potential Areas for Future Development):
- Limited to two SVG templates.
- Image generation quality and prompt engineering could still be improved for further optimization.
- Error handling could be enhanced.

## Version 1.1.2 - Refined Generation and Enhanced Text!🏆💯
**Infographic Generator v1.1.2 builds upon the streamlined download feature of v1.1.1 by incorporating crucial refinements to the infographic generation process. Minor prompt engineering changes lead to better content generation, while fixes for SVG text rendering ensure a more polished final product. We are committed to continuous improvement and look forward to bringing you even more exciting updates!**🎉🥳

### Next time
```sh
cd frontend
npm start
```

## Contribution🤝
Contributions are welcome! Feel free to submit issues or pull requests.

## License📄
This project is licensed under the MIT License.
