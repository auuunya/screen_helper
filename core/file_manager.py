import os

class FileManager:
    
    @staticmethod
    def read(file_path: str) -> str:
        """
        Read content from a specified file
        :param file_path: Path to the file
        :return: File content, returns an empty string if reading fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return ""

    @staticmethod
    def write(file_path: str, content: str) -> None:
        """
        Write content to a specified file
        :param file_path: Path to the file
        :param content: Content to be written to the file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise

    @staticmethod
    def append(file_path: str, content: str) -> None:
        """
        Append content to a specified file
        :param file_path: Path to the file
        :param content: Content to be appended to the file
        """
        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise

    @staticmethod
    def delete(file_path: str) -> None:
        """
        Delete a specified file
        :param file_path: Path to the file
        """
        try:
            os.remove(file_path)
        except Exception as e:
            raise
