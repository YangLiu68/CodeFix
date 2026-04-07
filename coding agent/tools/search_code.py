import os

def search_code(query: str, path: str = ".") -> str:
    """Searches for a string in all files within a directory."""
    results = []
    for root, dirs, files in os.walk(path):
        # Skip common ignore directories
        if any(ignored in root for ignored in [".git", "__pycache__", "venv", "node_modules"]):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append(f"{file_path}:{i+1}: {line.strip()}")
            except Exception:
                continue
    
    if not results:
        return f"No results found for '{query}'."
    
    return "\n".join(results[:50]) # Limit to 50 results
