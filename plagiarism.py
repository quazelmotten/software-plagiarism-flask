from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_cpp as tscpp
# import tree_sitter_javascript as tsjavascript  # if supported

import hashlib
from collections import defaultdict

# Language map
LANGUAGE_MAP = {
    'python': Language(tspython.language()),
    'cpp' : Language(tscpp.language())
}

def get_language(lang_code):
    if lang_code not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {lang_code}")
    return LANGUAGE_MAP[lang_code]

def tokenize_with_tree_sitter(file_path, lang_code='python'):
    language = get_language(lang_code)
    parser = Parser(language)
    

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parser.parse(bytes(code, 'utf-8'))
    tokens = []

    def extract_tokens(node):
        if len(node.children) > 0:
            for child in node.children:
                extract_tokens(child)
        else:
            tokens.append(node.type)

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
def analyze_plagiarism(file1, file2, language='python'):
    tokens1 = tokenize_with_tree_sitter(file1, language)
    tokens2 = tokenize_with_tree_sitter(file2, language)

    k_grams1 = generate_k_grams(tokens1)
    k_grams2 = generate_k_grams(tokens2)

    fingerprints1 = compute_fingerprints(k_grams1)
    fingerprints2 = compute_fingerprints(k_grams2)

    winnowed_fingerprints1 = winnow_fingerprints(fingerprints1)
    winnowed_fingerprints2 = winnow_fingerprints(fingerprints2)

    index1 = index_fingerprints(winnowed_fingerprints1, 1)
    index2 = index_fingerprints(winnowed_fingerprints2, 2)

    similarity = compute_similarity(index1, index2)
    return similarity