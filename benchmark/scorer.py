import re


def score_answer(answer: str, convention: str, expected_pattern: str) -> bool:
    """Check whether an agent's answer follows the expected convention.

    Args:
        answer: The agent's raw text response to a question.
        convention: The name of the convention being tested.
        expected_pattern: The pattern or keyword expected in a correct answer.

    Returns:
        True if the answer matches the expected convention, False otherwise.
    """
    if convention == "test_naming":
        return expected_pattern in answer

    if convention == "error_handling":
        return "AppError" in answer

    if convention == "docstring":
        return bool(re.search(r"Args:", answer)) and bool(re.search(r"Returns:", answer))

    if convention == "imports":
        # crude check: stdlib-style import appears before a local "app." import
        stdlib_idx = answer.find("import logging")
        local_idx = answer.find("from app")
        if stdlib_idx == -1 or local_idx == -1:
            return False
        return stdlib_idx < local_idx

    if convention == "logging":
        return "getLogger(__name__)" in answer

    return False