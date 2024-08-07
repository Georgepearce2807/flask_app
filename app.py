from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set up the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Create the uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Database models
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    modules = db.relationship('Module', backref='subject', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    files = db.relationship('File', backref='module', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(100), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)

# Routes
@app.route('/')
def index():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/upload/<int:module_id>', methods=['POST'])
def upload(module_id):
    module = Module.query.get_or_404(module_id)
    file = request.files.get('file')
    
    if not file or file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('index'))

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    new_file = File(filename=filename, filepath=filepath, module=module)
    db.session.add(new_file)
    db.session.commit()

    flash(f'File "{filename}" uploaded successfully!', 'success')
    return redirect(url_for('index'))

# Route to serve the files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize the database
@app.before_request
def create_tables():
    db.create_all()

if __name__ != "__main__":
    application = app

