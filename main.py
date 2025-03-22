import os
from flask import Flask, render_template, request, jsonify
import hashlib
from collections import defaultdict
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import difflib

app = Flask(__name__)

# Initialize the tree-sitter Python language
PY_LANGUAGE = Language(tspython.language())

# Ensure uploaded files are saved in a temporary directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to tokenize source code into a list of tokens using tree-sitter
def tokenize_with_tree_sitter(file_path):
    parser = Parser(PY_LANGUAGE)

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parser.parse(bytes(code, 'utf-8'))
    tokens = []

    def extract_tokens(node):
        # Recursively extract tokens from the AST
        if len(node.children) > 0:
            for child in node.children:
                extract_tokens(child)
        else:
            tokens.append(node.type)  # Capture the type of the token (e.g., keyword, identifier)

    extract_tokens(tree.root_node)
    return tokens

# Generate k-grams from tokenized source code
def generate_k_grams(tokens, k=3):
    k_grams = []
    for i in range(len(tokens) - k + 1):
        k_grams.append(tuple(tokens[i:i+k]))  # Create k-grams (tuples of k tokens)
    return k_grams

# Compute rolling hash for k-grams (using simple hash for illustration)
def compute_fingerprints(k_grams):
    fingerprints = []
    for k_gram in k_grams:
        fingerprint = hashlib.sha256(str(k_gram).encode('utf-8')).hexdigest()  # You can use any hash function
        fingerprints.append(fingerprint)
    return fingerprints

# Apply the Moss Winnowing algorithm to reduce the fingerprints
def winnow_fingerprints(fingerprints, window_size=5):
    winnowed = []
    for i in range(len(fingerprints) - window_size + 1):
        window = fingerprints[i:i+window_size]
        min_fingerprint = min(window)  # Choose the smallest fingerprint in the window
        if not winnowed or min_fingerprint != winnowed[-1]:  # Avoid duplicates
            winnowed.append(min_fingerprint)
    return winnowed

# Index fingerprints for fast comparison
def index_fingerprints(fingerprints, file_id):
    index = defaultdict(list)
    for position, fingerprint in enumerate(fingerprints):
        index[fingerprint].append((file_id, position))  # Store file_id and position
    return index

# Calculate similarity between two sets of indexed fingerprints
def compute_similarity(index_a, index_b):
    common_fingerprints = set(index_a.keys()) & set(index_b.keys())
    Sa = sum(len(index_a[fingerprint]) for fingerprint in common_fingerprints)
    Sb = sum(len(index_b[fingerprint]) for fingerprint in common_fingerprints)
    Ta = sum(len(index_a[fingerprint]) for fingerprint in index_a)
    Tb = sum(len(index_b[fingerprint]) for fingerprint in index_b)
    similarity = (Sa + Sb) / (Ta + Tb) if (Ta + Tb) > 0 else 0
    return similarity

# Helper function to analyze plagiarism between two files
def analyze_plagiarism(file1, file2):
    # Tokenize and generate fingerprints for both files
    tokens1 = tokenize_with_tree_sitter(file1)
    tokens2 = tokenize_with_tree_sitter(file2)
    print('got tokens')
    
    k_grams1 = generate_k_grams(tokens1)
    k_grams2 = generate_k_grams(tokens2)
    print('got kgrams')
    
    fingerprints1 = compute_fingerprints(k_grams1)
    fingerprints2 = compute_fingerprints(k_grams2)
    print('got fingerprints')
    
    # Apply Moss Winnowing
    winnowed_fingerprints1 = winnow_fingerprints(fingerprints1)
    winnowed_fingerprints2 = winnow_fingerprints(fingerprints2)
    print('got winnowed')
    
    # Index the fingerprints
    index1 = index_fingerprints(winnowed_fingerprints1, 1)  # Assuming file1 is file 1
    index2 = index_fingerprints(winnowed_fingerprints2, 2)  # Assuming file2 is file 2
    print('got indexes')
    
    # Calculate the similarity between the two files
    similarity = compute_similarity(index1, index2)
    print(similarity)
    return similarity

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "No files part"})

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "No file selected"})

    # Save the files temporarily
    temp_file1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
    temp_file2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)

    file1.save(temp_file1)
    file2.save(temp_file2)

    # Read the files
    with open(temp_file1, 'r', encoding='utf-8') as f1:
        code1 = f1.readlines()

    with open(temp_file2, 'r', encoding='utf-8') as f2:
        code2 = f2.readlines()

    # Perform line-by-line comparison using difflib
    diff = list(difflib.ndiff(code1, code2))
    
    # Send back the plagiarism percentage and the diff
    similarity = analyze_plagiarism(temp_file1, temp_file2)
    return jsonify({
        "plagiarism_percentage": similarity * 100,
        "diff": diff
    })


if __name__ == '__main__':
    app.run(debug=True)
