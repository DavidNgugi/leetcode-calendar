import os

def get_file_path(filename: str) -> str:
    # step out of current directory and iinto data directory
    return os.path.join(os.path.dirname(__file__), "..", "data", filename)