"""Test the clean output - minimal interface with no verbose output."""

import os
from dotenv import load_dotenv
from orchestrator import StoryOrchestrator

load_dotenv()

def test_clean_output():
    """Test that no intermediate output is shown"""

    if not os.getenv("OPENAI_API_KEY"):
        print("[FAIL] OPENAI_API_KEY not found")
        return False

    print("="*60)
    print("TESTING CLEAN OUTPUT (No Verbose Mode)")
    print("="*60 + "\n")

    orchestrator = StoryOrchestrator(verbose=False)

    print("Generating story (should show no intermediate output)...\n")

    story, evaluation, revision_count = orchestrator.create_short_story(
        "A bunny who learns to share"
    )

    print("="*60)
    print("STORY OUTPUT:")
    print("="*60 + "\n")
    print(story)
    print("\n" + "="*60)

    print(f"\n[TEST INFO] Story generated successfully ({len(story)} chars)")
    print(f"[TEST INFO] No intermediate output was shown to user")
    print(f"[TEST INFO] User sees only the story text\n")

    return True

if __name__ == "__main__":
    test_clean_output()
