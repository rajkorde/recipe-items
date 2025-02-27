import os

from loguru import logger


def write_to_file(text: str, file_path: str) -> None:
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
    except Exception as e:
        logger.error(f"Error writing to file: {e}")


def read_from_file(file_path: str) -> str:
    content = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        logger.error(f"Error writing to file: {e}")

    return content
