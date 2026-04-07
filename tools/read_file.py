import os

def read_file(file_path: str) -> str:
    """Reads the content of a file and returns it as a string."""
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(absolute_path):
        return f"Error: File '{file_path}' not found."
    
    try:
        with open(absolute_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
