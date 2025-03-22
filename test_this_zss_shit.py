import os
from flask import Flask, render_template, request, jsonify
import zss  # For Tree Edit Distance calculation
from zss import Node  # Import Node from zss
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


# Define the Python language using tree_sitter_python
PY_LANGUAGE = Language(tspython.language())

# Ensure uploaded files are saved in a temporary directory

# Convert tree-sitter AST to zss-compatible format

# Function to convert tree-sitter AST into a tokenized list
def tokenize_with_tree_sitter(tree):
    # Recursively traverse the tree to extract tokens
    def extract_tokens(node):
        tokens = []
        # If the node has children, recursively extract tokens
        if len(node.children) > 0:
            for child in node.children:
                tokens.extend(extract_tokens(child))
        else:
            # Extract the token from the node's text representation
            tokens.append(node.type)
        return tokens

    return extract_tokens(tree.root_node)  # Return tokenized representation

def generate_k_grams(tokens, k=3):
    k_grams = []
    for i in range(len(tokens) - k + 1):
        k_grams.append(tuple(tokens[i:i+k]))  # Create k-grams (tuples of k tokens)
    return k_grams

def compute_fingerprints(k_grams):
    fingerprints = []
    for k_gram in k_grams:
        fingerprint = hash(k_gram)  # You can use a more sophisticated hash function here
        fingerprints.append(fingerprint)
    return fingerprints

def winnow_fingerprints(fingerprints, window_size=5):
    winnowed = []
    for i in range(len(fingerprints) - window_size + 1):
        window = fingerprints[i:i+window_size]
        min_fingerprint = min(window)  # Choose the smallest fingerprint in the window
        if not winnowed or min_fingerprint != winnowed[-1]:  # Avoid duplicates
            winnowed.append(min_fingerprint)
    return winnowed

from collections import defaultdict

def index_fingerprints(fingerprints, file_id):
    index = defaultdict(list)
    for position, fingerprint in enumerate(fingerprints):
        index[fingerprint].append((file_id, position))  # Store file_id and position
    return index

def compute_similarity(index_a, index_b):
    common_fingerprints = set(index_a.keys()) & set(index_b.keys())
    Sa = sum(len(index_a[fingerprint]) for fingerprint in common_fingerprints)
    Sb = sum(len(index_b[fingerprint]) for fingerprint in common_fingerprints)
    Ta = sum(len(index_a[fingerprint]) for fingerprint in index_a)
    Tb = sum(len(index_b[fingerprint]) for fingerprint in index_b)
    similarity = (Sa + Sb) / (Ta + Tb) if (Ta + Tb) > 0 else 0
    return similarity


# Helper function to calculate Tree Edit Distance similarity between two files
def analyze_plagiarism(file1, file2):
    # Initialize the parser for Python language
    parser = Parser(PY_LANGUAGE)

    # Parse the first file
    with open(file1, 'r', encoding='utf-8') as f1:
        code1 = f1.read()
    tree1 = parser.parse(bytes(code1, 'utf-8'))

    # Parse the second file
    with open(file2, 'r', encoding='utf-8') as f2:
        code2 = f2.read()
    tree2 = parser.parse(bytes(code2, 'utf-8'))

    # Convert both ASTs to zss-compatible format
    tree1_zss = tree_to_zss_format(tree1)
    tree2_zss = tree_to_zss_format(tree2)
    print(tree1_zss)
    # Define the necessary functions for zss.distance
    def get_children(node):
        return node.children  # Return children of the node

    def insert_cost(node):
        return 1  # Simple cost model for insertion

    def remove_cost(node):
        return 1  # Simple cost model for removal

    def update_cost(a, b):
        return 1 if a != b else 0  # Simple cost model for updating

    # Calculate Tree Edit Distance using ZSS
    try:
        distance = zss.distance(tree1_zss, tree2_zss, get_children, insert_cost, remove_cost, update_cost)
    except Exception as e:
        print(f"Error during ZSS distance calculation: {e}")
        return None

    # Normalize the Tree Edit Distance to a plagiarism percentage
    max_distance = max(len(tree1_zss.children), len(tree2_zss.children))
    plagiarism_percentage = (1 - distance / max_distance) * 100 if max_distance > 0 else 100
    print(plagiarism_percentage)
    return plagiarism_percentage

def index():
    return render_template('index.html')

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
    # Analyze plagiarism using Tree Edit Distance
    plagiarism_percentage = analyze_plagiarism(temp_file1, temp_file2)

    return jsonify({"plagiarism_percentage": plagiarism_percentage})

if __name__ == '__main__':
    
    print(analyze_plagiarism('C:\\Users\\1\\Desktop\\flasktree\\uploads\\lab_1.py','C:\\Users\\1\\Desktop\\flasktree\\uploads\\lab1.py'))