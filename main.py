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

@app.route('/compare_all')
def compare_all():
    language = app.config.get('SELECTED_LANGUAGE', 'python')
    upload_dir = app.config['UPLOAD_FOLDER']
    files = os.listdir(upload_dir)

    results = []
    seen = set()

    for i, f1 in enumerate(files):
        for j, f2 in enumerate(files):
            if i >= j:
                continue  # avoid duplicates and self-comparison
            key = tuple(sorted([f1, f2]))
            if key in seen:
                continue
            seen.add(key)

            path1 = os.path.join(upload_dir, f1)
            path2 = os.path.join(upload_dir, f2)
            try:
                similarity, _ = plagiarism.analyze_plagiarism(path1, path2, language)
                results.append({
                    "file1": f1,
                    "file2": f2,
                    "similarity": round(similarity * 100, 2)
                })
            except Exception as e:
                results.append({
                    "file1": f1,
                    "file2": f2,
                    "similarity": 0,
                    "error": str(e)
                })

    return jsonify({"comparisons": results})


@app.route('/compare_files')
def compare_files():
    import colorsys
    import random
    import hashlib

    file1_name = request.args.get('file1')
    file2_name = request.args.get('file2')
    language = request.args.get('language', 'python')

    if not file1_name or not file2_name:
        return jsonify({'error': 'Missing file names'}), 400

    path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1_name)
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2_name)

    with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
        file1_lines = f1.read().splitlines()
        file2_lines = f2.read().splitlines()

    similarity, matches = plagiarism.analyze_plagiarism(path1, path2, language=language)

    # Build color palette algorithmically
    def generate_color(i):
        """Generate nice visually distinct colors using HSV space."""
        hue = (i * 0.6180339887) % 1.0  # golden ratio spacing
        light = 0.65 + 0.2 * ((i % 2) - 0.5)
        sat = 0.6 + 0.3 * ((i % 3) / 3)
        r, g, b = colorsys.hsv_to_rgb(hue, sat, light)
        return f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 0.35)"

    # Prepare structures to track line colors
    line_colors_1 = {}
    line_colors_2 = {}

    line_meta_1 = {}
    line_meta_2 = {}

    for i, match in enumerate(matches):
        color = generate_color(i)
        start1, end1 = match['file1']
        start2, end2 = match['file2']

        for l in range(start1, end1 + 1):
            line_meta_1[l] = {'color': color, 'match_id': i}
        for l in range(start2, end2 + 1):
            line_meta_2[l] = {'color': color, 'match_id': i}


    # Render lines with color-coded highlights
    def render_lines(lines, meta_map, file_side):
        html_lines = []
        for i, line in enumerate(lines):
            safe = (
                line.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace(" ", "&nbsp;")
            )

            if not line.strip():
                html_lines.append('<div class="code-line">&nbsp;</div>')
                continue

            if i in meta_map:
                color = meta_map[i]['color']
                match_id = meta_map[i]['match_id']
                safe = (
                    f'<span class="highlight match-{match_id}" '
                    f'data-match="{match_id}" '
                    f'data-side="{file_side}" '
                    f'style="background-color:{color};">'
                    f'{safe}</span>'
                )

            html_lines.append(f'<div class="code-line">{safe}</div>')
        return "\n".join(html_lines)

    html1 = render_lines(file1_lines, line_meta_1, "file1")
    html2 = render_lines(file2_lines, line_meta_2, "file2")


    return jsonify({
        "plagiarism_percentage": similarity * 100,
        "file1_contents": html1,
        "file2_contents": html2
    })


if __name__ == '__main__':
    app.run(debug=True)
