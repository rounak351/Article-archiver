# Article Archiver

**Article Archiver** is a Flask-based web application that uses Optical Character Recognition (OCR) to digitize and organize physical articles. Users can upload images or PDFs, extract editable text, and store them with tags and categories — making knowledge searchable, accessible, and permanent. This project is ideal for students, researchers, and readers who need an efficient way to manage articles and documents.

## Features
- **OCR Integration**: Extract text from scanned images or PDF files using Tesseract OCR.
- **Article Management**: Save articles with titles, tags, and categories for easy organization.
- **Search & Filter**: Quickly locate articles by searching with keywords or filtering by tags and categories.
- **Responsive Design**: A clean, minimal, and responsive interface that works well on both desktop and mobile devices.
- **User Authentication**: Secure login and registration to manage personal articles (if implemented).
- **Export Options**: Future plans for allowing articles to be exported to PDF or text files.

## Tech Stack
- **Backend**: Flask (Python web framework), Tesseract OCR (for text extraction from images), SQLite (for database)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap (for responsive design)
- **Other Tools**: Jinja2 Templates (Flask templating engine)

## Installation

To set up the project on your local machine, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rounak351/Article-archiver.git
   # Clone the repository
git clone https://github.com/rounak351/Article-archiver.git

# Navigate to the project directory
cd Article-archiver

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# Install Tesseract OCR:
# On macOS (using Homebrew):
brew install tesseract
# On Ubuntu/Debian:
sudo apt install tesseract-ocr
# On Windows:
# Download from https://github.com/tesseract-ocr/tesseract and follow installer instructions

# Run the Flask application
python app.py

# Once the app is running, open this in your browser
# http://127.0.0.1:5000

