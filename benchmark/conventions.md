\# Codebase Conventions (Ground Truth)



1\. \*\*Test file naming:\*\* `test\_<module>\_spec.py` (NOT `test\_<module>.py`)

2\. \*\*Error handling:\*\* Always raise custom `AppError(message, code)`. Never raise bare `Exception` or built-in errors directly.

3\. \*\*Docstrings:\*\* Google-style. Every function must have `Args:` and `Returns:` sections.

4\. \*\*Import order:\*\* stdlib imports, then third-party, then local — each group alphabetized, blank line between groups.

5\. \*\*Logging:\*\* Always `logger = logging.getLogger(\_\_name\_\_)` + structured logging calls. Never use `print()`.

