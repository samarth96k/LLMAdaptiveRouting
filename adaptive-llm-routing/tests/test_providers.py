"""Quick test of all 4 LLM providers."""
import os, sys
os.environ["PYTHONIOENCODING"] = "utf-8"

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import validate_keys
from src.llm_provider import invoke_with_fallback
from langchain_core.messages import HumanMessage

print("=" * 60)
print("PHASE 2 PROVIDER TEST")
print("=" * 60)

validate_keys()
test_msg = [HumanMessage(content="What is 2+2? Reply with just the number.")]

for role, provider_name in [("single_llm", "Groq"), ("multi_agent", "Mistral"), ("evaluation", "Mistral")]:
    print(f"\nTesting {provider_name} (role={role})...")
    try:
        resp, used = invoke_with_fallback(test_msg, role=role, max_retries=1)
        answer = resp.content.strip()[:50]
        print(f"  OK: {used} -> '{answer}'")
    except Exception as e:
        print(f"  FAIL: {str(e)[:120]}")

print("\nAll provider tests complete.")
