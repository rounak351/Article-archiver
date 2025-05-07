📚 Article Archiver
Article Archiver is a Flask-based web application that uses Optical Character Recognition (OCR) to digitize and organize physical articles. Users can upload images or PDFs, extract editable text, and store them with tags and categories — making knowledge searchable, accessible, and permanent.

This project is ideal for students, researchers, and readers who need an efficient way to manage articles and documents.

✨ Features
📷 OCR Integration – Extract text from scanned images or PDFs using Tesseract OCR.

🗂 Article Management – Save articles with titles, tags, and categories for easy organization.

🔎 Search & Filter – Quickly locate articles by searching with keywords or filtering by tags/categories.

📱 Responsive Design – Clean and minimal interface that works on both desktop and mobile.

🔐 User Authentication – Secure login and registration (planned/optional).

📤 Export Options – Future updates may include exporting articles to PDF or text.

🛠 Tech Stack
Backend: Flask (Python), Tesseract OCR, SQLite
Frontend: HTML5, CSS3, JavaScript, Bootstrap
Templating: Jinja2

🚀 Installation

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


📥 Install Tesseract OCR
macOS (Homebrew):brew install tesseract
Ubuntu/Debian:sudo apt install tesseract-ocr
Windows:https://github.com/tesseract-ocr/tesseract


▶️ Run the Application
python app.py


