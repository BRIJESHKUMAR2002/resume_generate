from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
import gemini
import chatgpt
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'processed', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'supersecretkey'


@app.route('/')
def index():
    # filedata_list = Files.query.all()
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def empty_folder(folder_path):
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(e)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'model' not in request.form:
        return jsonify({'message': 'No file or model part'}), 400

    file = request.files['file']
    model = request.form['model']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.rsplit('.', 1)[1].lower() == 'docx':
            loader = UnstructuredWordDocumentLoader(file_path)
        elif filename.rsplit('.', 1)[1].lower() == 'pdf':
            loader = PyPDFLoader(file_path)
        else:
            return jsonify({'message': 'Unsupported file format'}), 400
        datall = loader.load()
        Input = ''.join([page.page_content for page in datall])
        print(model)
        if model == "Gemini":
            gemini.gemini_process(Input, filename)
        else:
            chatgpt.chatgpt_process(Input, filename)

        output_filename = filename
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        empty_folder(UPLOAD_FOLDER)
        return jsonify({'filename': output_filename, 'url': url_for('uploaded_file', filename=output_filename)})
    else:
        return jsonify({'message': 'Allowed file types are pdf, docx'}), 400


@app.route('/processed/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
