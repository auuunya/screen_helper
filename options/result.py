class Result:
    """
    结果类，用于封装操作的结果信息。

    :param success: 表示操作是否成功的布尔值。
    :param data: 可选，操作成功时返回的数据。默认为 None。
    :param error: 可选，操作失败时的错误信息。默认为 None。

    示例:
        result = Result(success=True, data={"key": "value"})
        if result.success:
            print("操作成功:", result.data)
        else:
            print("操作失败:", result.error)
    """

    def __init__(self, success: bool, data=None, error=None):
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self):
        return f"<Result(success={self.success}, data={self.data}, error={self.error})>"

    def is_success(self) -> bool:
        """
        检查操作是否成功。

        :return: 如果操作成功，返回 True；否则返回 False。
        """
        return self.success

    def __bool__(self) -> bool:
        """
        支持布尔上下文的使用。

        :return: 如果操作成功，返回 True；否则返回 False。
        """
        return self.success is True
