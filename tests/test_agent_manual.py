from src.agent.agent import MemoardAgent

agent = MemoardAgent(persist_path="./chroma_db_manual", session_id="manual_test_session")

print("=== Teaching a convention ===")
answer1 = agent.answer(
    "I'm adding tests for the users/profile.py module. What should I name the test file? "
    "In this codebase, the rule is: test files must be named test_<module>_spec.py.",
    convention_tag="test_naming",
)
print("Agent:", answer1)

print("\n=== Testing recall (no hint given this time) ===")
answer2 = agent.answer(
    "I'm adding tests for a new shipping.py module. What should I name the test file?",
    convention_tag="test_naming",
)
print("Agent:", answer2)