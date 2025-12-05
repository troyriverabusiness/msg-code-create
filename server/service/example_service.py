"""Example service layer"""


def get_greeting(name: str = "World") -> dict:
    """
    Example service function that returns a greeting.

    Args:
        name: The name to greet

    Returns:
        A dictionary with a greeting message
    """
    return {"message": f"Hello, {name}!", "status": "success"}
