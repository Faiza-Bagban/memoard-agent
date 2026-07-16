from src.memory.stores import SemanticStore, ProceduralStore

semantic = SemanticStore(persist_path="./chroma_db_test_consolidation")
procedural = ProceduralStore(persist_path="./chroma_db_test_consolidation")

print("=== Semantic facts ===")
for item in semantic.all():
    print(f"- {item['content']}")

print("\n=== Procedural skills ===")
for item in procedural.all():
    print(f"- {item['content']}")