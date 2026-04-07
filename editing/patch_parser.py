import re

class PatchParser:
    """
    Parses SEARCH/REPLACE blocks from LLM responses.
    Format:
    <<<<<<< SEARCH
    old code
    =======
    new code
    >>>>>>> REPLACE
    """
    
    @staticmethod
    def parse(text: str):
        pattern = r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE"
        matches = re.findall(pattern, text, re.DOTALL)
        return [{"search": m[0], "replace": m[1]} for m in matches]
