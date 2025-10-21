"""Test setup and configuration without making API calls"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported"""
    print("\nTesting imports...")

    try:
        from bedtime_story_generator.core.models import NarrativePlan, JudgeEvaluation, ChapterContext
        print("[OK] models imported successfully")

        from bedtime_story_generator.agents import narrative_director, storyteller, judge, revision_agent
        print("[OK] agents imported successfully")

        from bedtime_story_generator.core.orchestrator import StoryOrchestrator
        print("[OK] orchestrator imported successfully")

        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dataclasses():
    """Test that dataclasses can be instantiated"""
    print("\nTesting dataclass instantiation...")

    try:
        from bedtime_story_generator.core.models import NarrativePlan, JudgeEvaluation, ChapterContext

        # Test NarrativePlan
        plan = NarrativePlan(
            story_category="adventure",
            story_arc="Hero's Journey",
            themes=["bravery", "friendship"],
            target_length="short",
            complexity_level="age 5-10",
            key_elements=["character growth"]
        )
        print(f"[OK] NarrativePlan created: {plan.story_category}")

        # Test JudgeEvaluation
        evaluation = JudgeEvaluation(
            overall_score=8.5,
            age_appropriate=True,
            feedback="Great story!",
            strengths=["engaging", "age-appropriate"],
            improvements_needed=[],
            needs_revision=False
        )
        print(f"[OK] JudgeEvaluation created: score={evaluation.overall_score}")

        # Test ChapterContext
        context = ChapterContext(
            chapter_number=1,
            previous_chapters=[],
            narrative_plan=plan,
            user_request="A brave knight"
        )
        print(f"[OK] ChapterContext created: chapter {context.chapter_number}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to create dataclasses: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_definitions():
    """Test that agents are properly defined"""
    print("\nTesting agent definitions...")

    try:
        from bedtime_story_generator.agents import narrative_director, storyteller, judge, revision_agent
        from agents import Agent

        # Verify all agents are Agent instances
        agents = {
            'NarrativeDirector': narrative_director,
            'Storyteller': storyteller,
            'Judge': judge,
            'RevisionAgent': revision_agent
        }

        for name, agent in agents.items():
            if isinstance(agent, Agent):
                print(f"[OK] {name} agent properly defined")
            else:
                print(f"[FAIL] {name} is not an Agent instance")
                return False

        return True
    except Exception as e:
        print(f"[FAIL] Failed to verify agents: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_init():
    """Test that orchestrator can be initialized"""
    print("\nTesting orchestrator initialization...")

    try:
        from bedtime_story_generator.core.orchestrator import StoryOrchestrator

        # Initialize orchestrator
        orchestrator = StoryOrchestrator(show_spinner=False)
        print(f"[OK] StoryOrchestrator initialized (max_revisions={orchestrator.max_revisions})")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("RUNNING COST-EFFICIENT SETUP TESTS")
    print("="*60 + "\n")

    tests = [
        test_imports,
        test_dataclasses,
        test_agent_definitions,
        test_orchestrator_init
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n" + "="*60)
    if all(results):
        print("ALL TESTS PASSED - Setup is ready!")
        print("="*60)
        return 0
    else:
        print("SOME TESTS FAILED - Check errors above")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
