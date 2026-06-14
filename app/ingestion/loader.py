import os
from typing import List, Dict

def load_markdown_files(directory: str) -> List[Dict[str, str]]:
    """
    Loads all markdown files from a given directory.
    Returns a list of dicts with 'content' and 'source'.
    """
    documents = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        documents.append({
                            "content": f.read(),
                            "source": file_path
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return documents
