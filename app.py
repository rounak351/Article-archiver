from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os
import pytesseract
from PIL import Image
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import PyPDF2
from docx import Document
from pdf2image import convert_from_path

# Initialize Flask app
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize database
def init_db():
    with sqlite3.connect('articles.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE,
                     password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS articles (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     filename TEXT,
                     text TEXT,
                     category TEXT,
                     user_id INTEGER,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()

init_db()

# Add default admin user
def add_default_user():
    with sqlite3.connect('articles.db') as conn:
        c = conn.cursor()
        username = 'admin'
        password = generate_password_hash('password123')  # Default password
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("Default admin user added successfully!")
        except sqlite3.IntegrityError:
            print("Default admin user already exists!")

add_default_user()

# OCR Function
def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return f"Error extracting text from image: {e}"

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return f"Error extracting text from PDF: {e}"

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        return f"Error extracting text from DOCX: {e}"

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return text
    except Exception as e:
        logging.error(f"Error extracting text from TXT: {e}")
        return f"Error extracting text from TXT: {e}"

# User Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            with sqlite3.connect('articles.db') as conn:
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    flash("Registration successful! Please log in.")
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    flash("Username already exists!")
                    return redirect(url_for('register'))
        return render_template('register.html')
    except Exception as e:
        logging.error(f"Error in register route: {e}")
        return "Internal Server Error", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('articles.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]  # Store username in session
                flash('Logged in successfully!')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!")
    return redirect(url_for('login'))

# Home Route
@app.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        with sqlite3.connect('articles.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM articles WHERE user_id = ?", (session['user_id'],))
            articles = c.fetchall()
            print(f"Articles fetched: {articles}")
        return render_template('home.html', articles=articles)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

# Upload Route
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if 'file' not in request.files:
            flash("No file part")
            return redirect(url_for('index'))
        
        file = request.files['file']
        category = request.form.get('category', 'Uncategorized')
        
        if file.filename == '':
            flash("No selected file")
            return redirect(url_for('index'))
            
        # Check file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.docx', '.txt'}
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            flash(f"Unsupported file type: {file_ext}. Supported types are: {', '.join(allowed_extensions)}")
            return redirect(url_for('index'))
            
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            # Extract text based on file type
            text = ''
            try:
                if file_ext in {'.png', '.jpg', '.jpeg'}:
                    text = extract_text(filepath)  # OCR for images
                elif file_ext == '.pdf':
                    text = extract_text_from_pdf(filepath)  # PDF text extraction
                elif file_ext == '.docx':
                    text = extract_text_from_docx(filepath)  # DOCX text extraction
                elif file_ext == '.txt':
                    text = extract_text_from_txt(filepath)  # TXT text extraction
            except Exception as e:
                logging.error(f"Error extracting text: {e}")
                flash(f"Error extracting text from file: {str(e)}")
                return redirect(url_for('index'))

            # Save to database
            print(f"Saving to database: {text}")
            with sqlite3.connect('articles.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO articles (filename, text, category, user_id) VALUES (?, ?, ?, ?)", 
                         (file.filename, text, category, session['user_id']))
                conn.commit()
            flash("File uploaded and text extracted successfully!")
            return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error in upload route: {e}")
        flash(f"Error uploading file: {str(e)}")
        return redirect(url_for('index'))

# Search Route
@app.route('/search', methods=['GET'])
def search():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        query = request.args.get('query', '').strip().lower()
        if not query:
            return redirect(url_for('index'))
        
        with sqlite3.connect('articles.db') as conn:
            c = conn.cursor()
            
            # Search for exact word matches in both text and category fields
            sql = """
                SELECT * FROM articles 
                WHERE (
                    LOWER(text) LIKE ? OR 
                    LOWER(category) LIKE ?
                ) 
                AND user_id = ?
                ORDER BY 
                    CASE 
                        WHEN LOWER(category) LIKE ? THEN 1
                        WHEN LOWER(text) LIKE ? THEN 2
                        ELSE 3
                    END
            """
            # Add spaces around the search term to match exact words
            search_pattern = f'% {query} %'
            params = (search_pattern, search_pattern, session['user_id'], search_pattern, search_pattern)
            
            c.execute(sql, params)
            results = c.fetchall()
            
            if not results:
                flash(f"No results found for: {query}")
            else:
                flash(f"Found {len(results)} results for: {query}")
                
        return render_template('home.html', articles=results)
    except Exception as e:
        logging.error(f"Error in search route: {e}")
        flash("Error performing search")
        return redirect(url_for('index'))

# Download Route
@app.route('/download/<filename>')
def download(filename):
    try:
        # Set the correct MIME type based on file extension
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        
        file_ext = os.path.splitext(filename)[1].lower()
        mime_type = mime_types.get(file_ext, 'application/octet-stream')
        
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            mimetype=mime_type
        )
    except Exception as e:
        logging.error(f"Error in download route: {e}")
        flash("Error displaying file")
        return redirect(url_for('index'))

@app.route('/view_text/<int:article_id>')
def view_text(article_id):
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        with sqlite3.connect('articles.db') as conn:
            c = conn.cursor()
            c.execute("SELECT filename, text, category FROM articles WHERE id = ? AND user_id = ?", 
                     (article_id, session['user_id']))
            article = c.fetchone()
            if article:
                return render_template('view_text.html', 
                                    filename=article[0], 
                                    text=article[1], 
                                    category=article[2])
            else:
                flash("Article not found")
                return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error viewing text: {e}")
        flash("Error viewing text")
        return redirect(url_for('index'))

@app.route('/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        filename = request.form.get('filename')
        if not filename:
            flash("Filename not provided")
            return redirect(url_for('index'))
            
        with sqlite3.connect('articles.db') as conn:
            c = conn.cursor()
            
            # Verify the article belongs to the current user
            c.execute("SELECT filename FROM articles WHERE id = ? AND user_id = ?", 
                     (article_id, session['user_id']))
            article = c.fetchone()
            
            if not article:
                flash("Article not found or you don't have permission to delete it")
                return redirect(url_for('index'))
                
            # Delete from database
            c.execute("DELETE FROM articles WHERE id = ? AND user_id = ?", 
                     (article_id, session['user_id']))
            conn.commit()
            
            # Delete the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
            flash("Article deleted successfully")
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Error deleting article: {e}")
        flash("Error deleting article")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)