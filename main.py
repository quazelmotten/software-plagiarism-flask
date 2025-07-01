import os
from flask import Flask, render_template, request, jsonify
import difflib
import plagiarism

app = Flask(__name__)

# Ensure uploaded files are saved in a temporary directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('files')
    saved_filenames = []
    language = request.form.get('language', 'python')  # Default to Python

    for file in uploaded_files:
        if file:  # (Optional) adapt this to language
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            saved_filenames.append(file.filename)

    # Store language selection in a global dictionary or session
    app.config['SELECTED_LANGUAGE'] = language

    return jsonify({'files': saved_filenames})


@app.route('/compare_files')
def compare_files():
    file1_name = request.args.get('file1')
    file2_name = request.args.get('file2')
    language = request.args.get('language', 'python')  # <-- add this line

    if not file1_name or not file2_name:
        return jsonify({'error': 'Missing file names'}), 400

    path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1_name)
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2_name)

    with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
        file1_contents = f1.read()
        file2_contents = f2.read()

    similarity = plagiarism.analyze_plagiarism(path1, path2, language=language)  # <-- use dynamic language


    diff_output_file1 = []
    diff_output_file2 = []

    for line in difflib.ndiff(file1_contents.splitlines(), file2_contents.splitlines()):
        if line.startswith('+ '):
            content = line[2:].replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
            diff_output_file1.append('<div class="code-line placeholder">&nbsp;</div>')
            diff_output_file2.append(f'<div class="code-line green">{content}</div>')
        elif line.startswith('- '):
            content = line[2:].replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
            diff_output_file1.append(f'<div class="code-line red">{content}</div>')
            diff_output_file2.append('<div class="code-line placeholder">&nbsp;</div>')
        else:
            content = line[2:].replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
            diff_output_file1.append(f'<div class="code-line">{content}</div>')
            diff_output_file2.append(f'<div class="code-line">{content}</div>')

    return jsonify({
        "plagiarism_percentage": similarity * 100,
        "file1_contents": '<br>'.join(diff_output_file1),
        "file2_contents": '<br>'.join(diff_output_file2)
    })

if __name__ == '__main__':
    app.run(debug=True)
