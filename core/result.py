class Result:
    """
    Result class for encapsulating the outcome of an operation.

    :param success: A boolean indicating whether the operation was successful.
    :param data: Optional, data returned when the operation is successful. Defaults to None.
    :param error: Optional, error message when the operation fails. Defaults to None.

    Example:
        result = Result(success=True, data={"key": "value"})
        if result.success:
            print("Operation successful:", result.data)
        else:
            print("Operation failed:", result.error)
    """

    def __init__(self, success: bool, data=None, error=None):
        """
        Initialize a Result object.

        :param success: Boolean indicating if the operation succeeded.
        :param data: Optional data associated with a successful operation.
        :param error: Optional error message in case of failure.
        """
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self):
        """
        Return a string representation of the Result object.

        :return: A string showing the success, data, and error.
        """
        return f"<Result(success={self.success}, data={self.data}, error={self.error})>"

    def is_success(self) -> bool:
        """
        Check if the operation was successful.

        :return: True if the operation was successful, False otherwise.
        """
        return self.success

    def __bool__(self) -> bool:
        """
        Support for boolean context.

        :return: True if the operation was successful, False otherwise.
        """
        return self.success is True
