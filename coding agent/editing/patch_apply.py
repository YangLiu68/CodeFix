import os

def apply_patch(file_path: str, search_text: str, replace_text: str) -> str:
    """
    Applies a search/replace patch to a file.
    Returns a detailed status message so the agent knows if it worked.
    """
    if not os.path.exists(file_path):
        return f"ERROR: File '{file_path}' does not exist."

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if search_text not in content:
        # Give the agent a clue: show nearby lines to help it adjust
        lines = content.splitlines()
        first_search_line = search_text.strip().splitlines()[0].strip() if search_text.strip() else ""
        nearby = [l for l in lines if first_search_line[:20] in l] if first_search_line else []
        hint = f"\nHint – similar lines found:\n" + "\n".join(nearby[:5]) if nearby else "\nHint: no similar lines found. Use read_file to check the current file content before patching."
        return (
            f"ERROR: search_text not found in '{file_path}'. Patch NOT applied.\n"
            f"The file may have changed. Call read_file('{file_path}') first to get the current content, "
            f"then retry with the exact text.{hint}"
        )

    new_content = content.replace(search_text, replace_text, 1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Verify by re-reading
    with open(file_path, 'r', encoding='utf-8') as f:
        verify = f.read()

    if replace_text in verify:
        return f"SUCCESS: Patch applied to '{file_path}'. The replacement is confirmed in the file."
    else:
        return f"WARNING: Patch was written but verification failed for '{file_path}'."
