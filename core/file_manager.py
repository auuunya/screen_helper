# TODO: coding
class FileManager:
    @staticmethod
    def read(file_path: str) -> str:
        """
        从指定文件读取内容
        :param file_path: 文件路径
        :return: 文件内容，如果读取失败则返回空字符串
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return ""

    @staticmethod
    def write(file_path: str, content: str):
        """
        将内容写入指定文件
        :param file_path: 文件路径
        :param content: 要写入文件的内容
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise

    @staticmethod
    def append(file_path: str, content: str):
        """
        将内容追加到指定文件
        :param file_path: 文件路径
        :param content: 要追加到文件的内容
        """
        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise

    @staticmethod
    def delete(file_path: str):
        """
        删除指定文件
        :param file_path: 文件路径
        """
        try:
            os.remove(file_path)
        except Exception as e:
            raise