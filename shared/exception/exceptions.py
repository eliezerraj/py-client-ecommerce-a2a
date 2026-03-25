# exception/exceptions.py

class A2ARouterError(Exception):
    """Raised when an A2A Router message is not supported."""
    pass

class ToolValidationError(Exception):
    """Custom exception to abort tool calls immediately."""
    pass