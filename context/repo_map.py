import os

class RepoMap:
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        self.ignore_dirs = {".git", "__pycache__", "venv", "node_modules", ".vscode", ".idea"}

    def get_repo_structure(self) -> str:
        """Generates a text-based tree structure of the repository."""
        structure = []
        for root, dirs, files in os.walk(self.root_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            level = root.replace(self.root_path, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root)
            if folder_name:
                structure.append(f"{indent}📁 {folder_name}/")
            else:
                structure.append(f"📁 [Project Root]")
                
            sub_indent = '  ' * (level + 1)
            for f in files:
                if f.endswith(('.py', '.js', '.md', '.txt', '.toml', '.json')):
                    structure.append(f"{sub_indent}📄 {f}")
        
        return "\n".join(structure)

    def get_summary(self) -> str:
        """Returns a summary of the repository for LLM context."""
        tree = self.get_repo_structure()
        summary = f"Repository Structure:\n\n{tree}\n"
        return summary

if __name__ == "__main__":
    rm = RepoMap()
    print(rm.get_summary())
