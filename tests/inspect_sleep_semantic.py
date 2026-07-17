from src.memory.stores import SemanticStore

semantic = SemanticStore(persist_path="./chroma_db_sleep")

print("=== All semantic facts (with importance + timestamp) ===")
for item in semantic.all():
    print(f"- {item['content']}")
    print(f"  (importance={item['metadata'].get('importance')}, timestamp={item['metadata'].get('timestamp')})")
    print()