
# Caption Generator - Backend + Frontend

This project provides an AI-powered image caption generator.

## Backend
- Flask server (port 7860)
- Hugging Face BLIP model (Salesforce/blip-image-captioning-base)
- Requires API token for requests: r8_4nOth0dOBOXUr9QSVL2Rl0QhD1zLcby4ZSWDT

### Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

## Frontend
Open `src/index.html` in a browser (or use VS Code Live Server).

Workflow:
1. Select/upload an image.
2. The image is sent to backend `/upload`.
3. Backend stores it, then `/generate_caption` creates AI caption.
4. Caption displayed on page.

# AI Image Caption Generator

An AI web application that automatically generates captions for uploaded images using the BLIP Transformer model.

## Features

• Upload any image  
• AI generates natural language caption  
• Modern web interface  
• GPU acceleration support  
• Flask backend  

## Tech Stack

Python  
Flask  
PyTorch  
Transformers  
BLIP Model  
TailwindCSS  

## Installation

Clone the repository
