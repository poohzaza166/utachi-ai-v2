import spacy
from spacy.lang.en.examples import sentences
from typing import List

class TreeNode:
    def __init__(self, token):
        self.token = token
        self.children: List[TreeNode] = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"TreeNode(text='{self.token.text}', pos='{self.token.pos_}', dep='{self.token.dep_}')"

def build_dependency_tree(doc):
    # Create a dictionary to store nodes
    nodes = {token: TreeNode(token) for token in doc}
    root = None

    # Build the tree structure
    for token in doc:
        if token.dep_ == "ROOT":
            root = nodes[token]
        else:
            nodes[token.head].add_child(nodes[token])

    return root

def print_tree(node, level=0):
    print("  " * level + str(node))
    for child in node.children:
        print_tree(child, level + 1)

# Load the English language model
nlp = spacy.load("en_core_web_trf")

# Process the first example sentence
doc = nlp(sentences[0])

# Build the dependency tree
root = build_dependency_tree(doc)

# Print the original sentence
print("Original sentence:")
print(doc.text)
print("\nDependency Tree:")

# Print the tree structure
print_tree(root)
if __name__ == "__main__":
    print("test")