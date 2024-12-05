from typing import List, Dict, Any, Callable
import uuid

class ScreenHelper:
    """
    This class provides methods for automating screen operations, including adding action methods,
    generating execution IDs, and managing the results of actions.

    Attributes:
        action_method_mapping (Dict[str, Callable[..., Any]]): A dictionary that maps action types to their corresponding methods.
        debug (bool): A flag to enable or disable debug mode.

    Methods:
        add_action_method: Adds a new action method to the action method mapping.
        generate_execute_id: Generates a unique execution ID.
        _add_processed_action_result: Adds or updates the result of an executed action.
        _add_value_to_processed_action: Adds a value to a specific key in the processed action results.
        get_execute_result: Retrieves the result of a specific action, optionally by key.
        _execute_action: Executes an action based on its type and options, and records the result.
        run_single_action: Runs a single action from a dictionary containing the action type and parameters.
        run_action_queue: Runs a queue of actions, processing each one sequentially.
    """

    # Class attributes
    action_method_mapping: Dict[str, Callable[..., Any]] = {}
    debug: bool = False

    def __init__(self):
        """
        Initializes the ScreenHelper class for automating screen operations.
        """
        self.processed_actions: Dict[str, Dict[str, Any]] = {}
        self.pending_actions: List[Dict[str, Any]] = []

    @classmethod
    def add_action_method(cls, action_type: str, method: Callable[..., Any] = None):
        """
        Dynamically adds a new action type and its corresponding method to the action mapping.
        Supports both single and batch additions.

        :param action_type: The action type as a string, or a dictionary of {action_type: method}.
        :param method: The method to associate with the action type. Should accept expected parameters and return valid results.
        :raises ValueError: If the action_type already exists in the mapping.
        :raises TypeError: If the provided method is not callable.
        """
        # If a dictionary is passed, add methods in bulk
        if isinstance(action_type, dict):
            for act_type, meth in action_type.items():
                cls._add_single_action_method(act_type, meth)
        # If a single method is passed, add it
        else:
            cls._add_single_action_method(action_type, method)

    @classmethod
    def _add_single_action_method(cls, action_type: str, method: Callable[..., Any]):
        """
        Adds a single action type and its method to the action method mapping.

        :param action_type: The action type to add.
        :param method: The method corresponding to the action type.
        :raises TypeError: If the method is not callable.
        :raises ValueError: If the action_type already exists in the mapping.
        """
        if not callable(method):
            raise TypeError(f"The method for action type '{action_type}' must be callable.")
        if action_type in cls.action_method_mapping:
            raise ValueError(f"Action type '{action_type}' is already in the action method mapping.")
        cls.action_method_mapping[action_type] = method

    def generate_execute_id(self) -> str:
        """
        Generates a unique execution identifier (UUID).

        :return: A string representing the generated UUID.
        """
        return str(uuid.uuid4())

    def _add_processed_action_result(self, execute_id: str, result: Dict[str, Any]):
        """
        Adds or updates the execution result for a given execution ID.

        :param execute_id: The unique identifier for the execution.
        :param result: A dictionary containing the result of the execution.
        """
        self.processed_actions.setdefault(execute_id, {}).update(result)

    def _add_value_to_processed_action(self, execute_id: str, key: str, value: Any):
        """
        Adds a value to a specific key in the processed actions dictionary. 
        If the key is already a dictionary, the value is merged.

        :param execute_id: The execution ID to update.
        :param key: The key to update in the processed actions dictionary.
        :param value: The value to add to the specified key.
        :raises KeyError: If the execution ID does not exist.
        """
        if execute_id in self.processed_actions:
            entry = self.processed_actions[execute_id]
            if key in entry:
                if isinstance(entry[key], dict) and isinstance(value, dict):
                    entry[key].update(value) 
                else:
                    entry[key] = value 
            else:
                entry[key] = value
        else:
            raise KeyError(f"Execution ID '{execute_id}' not found in processed actions.")
        
    def get_execute_result(self, execute_id: str, key: str = None) -> Any:
        """
        Retrieves the execution result for a specific execution ID, optionally by a specific key.

        :param execute_id: The unique identifier for the execution.
        :param key: An optional key to retrieve a nested value (supports dot notation).
        :return: The value associated with the specified key or the entire execution result.
        :raises KeyError: If the execution ID or key does not exist.
        """
        if execute_id in self.processed_actions:
            entry = self.processed_actions[execute_id]
            if key:
                keys = key.split('.')
                value = entry
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        raise KeyError(f"Execution ID '{execute_id}' not found for key '{key}'.")
                return value
            return entry
        raise KeyError(f"Execution ID '{execute_id}' not found in processed actions.")

    def _execute_action(self, action_type_text: str, options: Dict[str, Any], execute_id: str) -> bool:
        """
        Executes a specified action and records the result.

        :param action_type_text: The type of action to execute.
        :param options: A dictionary of options to pass to the action method.
        :param execute_id: The unique identifier for this execution.
        :return: True if the action was successful, or an error message if it failed.
        :raises ValueError: If the action type is not found.
        :raises TypeError: If the options are not provided as a dictionary.
        """
        method = self.action_method_mapping.get(action_type_text)
        if not method:
            raise ValueError(f"Unknown action type: {action_type_text}")
        if not isinstance(options, dict):
            raise TypeError(f"Options for action '{action_type_text}' should be a dictionary, but got {type(options).__name__}")
        
        retry_count = options.pop('retry_count', 3)
        attempts = 0
        attempt_errors = []
        while attempts <= retry_count:
            try:
                result = method(**options)
                self._add_processed_action_result(
                    execute_id=execute_id,
                    result={
                        "status": "success",
                        "action": {"action_type_text": action_type_text, "options": options},
                        "result": result
                    }
                )
                return True
            except Exception as e:
                attempts += 1
                attempt_errors.append(f"Attempt {attempts}/{retry_count} failed: {str(e)}")
        error_message = f"Error executing action '{action_type_text}' options: {options}, retries: {attempt_errors}"
        if self.debug:
            raise RuntimeError(error_message)
        return error_message

    def run_single_action(self, action: Dict[str, Any]) -> bool:
        """
        Executes a single action, typically from a dictionary containing action type and parameters.

        :param action: A dictionary containing the action type and its options.
        :return: The result of the action execution, either success or error message.
        """
        action_type_text = action.get("action_type_text")
        options = action.get("options", {})
        execute_id = options.get("execution_id", self.generate_execute_id())
        return self._execute_action(action_type_text, options, execute_id)

    def run_action_queue(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes a queue of actions sequentially, processing each one in order.

        :param actions: A list of dictionaries, each containing an action and its options.
        :return: A dictionary containing the processed actions and any pending actions.
        """
        self.pending_actions = actions.copy()
        while self.pending_actions:
            action = self.pending_actions.pop(0)
            action_type_text = action.get("action_type_text")
            options = action.get("options", {})
            execute_id = options.get("execution_id", self.generate_execute_id())
            result = self._execute_action(action_type_text, options, execute_id)
            if result is True:
                continue
            else:
                action["error"] = result
                self.pending_actions.insert(0, action)
                break
        return {
            "processed_actions": self.processed_actions,
            "pending_actions": self.pending_actions
        }
