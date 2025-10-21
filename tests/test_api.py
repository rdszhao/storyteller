"""Cost-efficient API test - generates one short story to verify the system works."""

import os
from dotenv import load_dotenv
from orchestrator import StoryOrchestrator

def test_short_story_generation():
    """Test short story generation with a simple request"""

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("[FAIL] OPENAI_API_KEY not found in environment")
        print("Please set it in .env file or export it")
        return False

    print("="*60)
    print("TESTING SHORT STORY GENERATION")
    print("="*60 + "\n")

    # Simple story request
    test_request = "A bunny who learns to share"

    print(f"Test Request: '{test_request}'")
    print("\nInitializing orchestrator...\n")

    # Create orchestrator with verbose output
    orchestrator = StoryOrchestrator(verbose=True)

    try:
        # Generate short story
        story, evaluation, revision_count = orchestrator.create_short_story(test_request)

        # Display results
        print("\n" + "="*60)
        print("GENERATED STORY")
        print("="*60 + "\n")
        print(story)
        print("\n" + "="*60)
        print(f"Quality Score: {evaluation.overall_score}/10")
        print(f"Age-Appropriate: {evaluation.age_appropriate}")
        print(f"Revisions: {revision_count}")
        print(f"Strengths: {', '.join(evaluation.strengths)}")
        if evaluation.improvements_needed:
            print(f"Improvements: {', '.join(evaluation.improvements_needed)}")
        print("="*60 + "\n")

        # Validate results
        assert len(story) > 100, "Story too short"
        assert evaluation.overall_score >= 0, "Invalid score"
        assert evaluation.age_appropriate, "Story not age-appropriate!"

        print("[OK] ALL VALIDATIONS PASSED!")
        print(f"Story length: {len(story)} characters")
        print(f"Story word count: ~{len(story.split())} words")

        return True

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_short_story_generation()
    exit(0 if success else 1)
