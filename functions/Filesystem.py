import os
from pathlib import Path

def createDirectory(path: Path):
    """
    Creates a directory if it does not exist
    """

    if not os.path.exists(path):
        os.makedirs(path)
    return path

