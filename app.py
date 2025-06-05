from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
import random
import string
import time
import configparser
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load configuration
config = configparser.ConfigParser()
config.read('conf.ini')
DATABASE = config['settings']['database']

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_random_code(length=4):
    return ''.join(random.choices(string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/submit', methods=['POST'])
def submit():
    content = request.form.get('content', '')
    client_pc = request.remote_addr
    client_user = request.form.get('user', '').strip()
    file = request.files.get('file')
    file_name = None
    file_path = None

    if not client_user:
        if request.accept_mimetypes['application/json']:
            return jsonify({'error': 'Username is required'}), 400
        else:
            return render_template('index.html', error='Username is required')

    if len(content) > 1024:
        if request.accept_mimetypes['application/json']:
            return jsonify({'error': 'Content exceeds 1024 bytes limit'}), 400
        else:
            return render_template('index.html', error='Content exceeds 1024 bytes limit')

    if file and file.filename:
        file_name = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        # Store relative path for serving
        file_path = f'uploads/{file_name}'

    random_code = generate_random_code()
    timestamp = int(time.time())

    with get_db() as conn:
        conn.execute('''
            INSERT INTO clips (code, content, file_name, file_path, timestamp, client_pc, client_user)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (random_code, content, file_name, file_path, timestamp, client_pc, client_user))
    
    if request.accept_mimetypes['application/json']:
        return jsonify({'code': random_code})
    else:
        return render_template('index.html', random_code=random_code)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    with get_db() as conn:
        # Get all file paths before deleting records
        rows = conn.execute('SELECT file_path FROM clips WHERE file_path IS NOT NULL').fetchall()
        for row in rows:
            file_path = row['file_path']
            if file_path:
                abs_path = os.path.join(os.path.dirname(__file__), file_path.replace('/', os.sep))
                if os.path.exists(abs_path):
                    try:
                        os.remove(abs_path)
                    except Exception as e:
                        print(f"Failed to delete {abs_path}: {e}")
        conn.execute('DELETE FROM clips')
    return render_template('history.html', history=[])

@app.route('/retrieve/<code>', methods=['GET'])
def retrieve(code):
    current_time = int(time.time())
    expiry = int(config['settings'].get('content_expiry', '300').split(';')[0].strip())    
    with get_db() as conn:        
        row = conn.execute(
            'SELECT content, file_name, file_path, timestamp FROM clips WHERE code = ? AND timestamp >= ?',
            (code, current_time - expiry)
        ).fetchone()
    if row:
        result = {'content': row['content']}
        if row['file_name'] and row['file_path']:
            result['file_name'] = row['file_name']
            result['file_url'] = '/' + row['file_path']
        return jsonify(result)
    else:
        return jsonify({'error': 'Code not found or expired'}), 404

@app.route('/history')
def history():
    current_time = int(time.time())
    expiry = int(config['settings'].get('content_expiry', '300').split(';')[0].strip())
    with get_db() as conn:
        rows = conn.execute(
            'SELECT timestamp, client_pc, client_user, code, content, file_name FROM clips WHERE timestamp >= ? ORDER BY timestamp DESC',
            (current_time - expiry,)
        ).fetchall()
    history = [
        {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['timestamp'])),
            'client_pc': row['client_pc'],
            'client_user': row['client_user'],
            'random_code': row['code'],
            'text_content': row['content'],
            'file_name': row['file_name']
        }
        for row in rows
    ]
    return render_template('history.html', history=history)

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                content TEXT,
                file_name TEXT,
                file_path TEXT,
                timestamp INTEGER,
                client_pc TEXT,
                client_user TEXT
            )
        ''')
    print("Database initialized.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)