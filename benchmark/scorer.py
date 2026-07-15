import re

STDLIB_MODULES = {
    "logging", "datetime", "os", "sys", "json", "re", "typing", "collections",
    "itertools", "functools", "pathlib", "uuid", "time", "math", "random",
    "subprocess", "threading", "asyncio", "enum", "dataclasses", "abc",
}

THIRDPARTY_MODULES = {
    "fastapi", "requests", "pydantic", "chromadb", "httpx", "streamlit",
    "langgraph", "langchain", "numpy", "pandas", "sentence_transformers",
}


def _classify_import_line(line: str) -> str:
    """Classify a single import line as stdlib, thirdparty, or local.

    Args:
        line: A single import statement line.

    Returns:
        One of "stdlib", "thirdparty", "local", or "unknown".
    """
    match = re.match(r"^\s*(?:from|import)\s+([\w\.]+)", line)
    if not match:
        return "unknown"
    root = match.group(1).split(".")[0]
    if root in STDLIB_MODULES:
        return "stdlib"
    if root in THIRDPARTY_MODULES:
        return "thirdparty"
    return "local"


def _check_import_order(answer: str) -> bool:
    """Check whether import lines in the answer follow stdlib -> thirdparty -> local order.

    Args:
        answer: The agent's raw text response.

    Returns:
        True if imports are correctly ordered, False otherwise.
    """
    lines = [l for l in answer.splitlines() if re.match(r"^\s*(from|import)\s+", l)]
    if not lines:
        return False
    order_rank = {"stdlib": 0, "thirdparty": 1, "local": 2}
    ranks = [order_rank.get(_classify_import_line(l), 3) for l in lines]
    return ranks == sorted(ranks)


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
        return _check_import_order(answer)

    if convention == "logging":
        return "getLogger(__name__)" in answer

    return False