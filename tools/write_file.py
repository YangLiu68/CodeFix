import os

def write_file(file_path: str, content: str) -> str:
    """Writes content to a file. Overwrites if it exists."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}."
    except Exception as e:
        return f"Error writing file: {str(e)}"
