"""Test the feedback logging system without making API calls"""

import os
import json
import shutil
from feedback_logger import FeedbackLogger
from models import NarrativePlan, JudgeEvaluation

def test_feedback_logger():
    """Test the FeedbackLogger class"""
    print("[Testing FeedbackLogger]")

    # Create test logger with temporary directory
    test_dir = "test_feedback_logs"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    logger = FeedbackLogger(log_dir=test_dir)

    # Test 1: Start session
    print("  Testing start_session...")
    session_id = logger.start_session("A bunny who learns to share", "short")
    assert session_id is not None
    assert logger.current_session is not None
    assert logger.current_session["user_request"] == "A bunny who learns to share"
    print("    [OK] Session started")

    # Test 2: Log narrative plan
    print("  Testing log_narrative_plan...")
    plan = NarrativePlan(
        story_category="adventure",
        story_arc="hero's journey",
        themes=["sharing", "friendship"],
        target_length="short",
        complexity_level="age 5-10",
        key_elements=["bunny character", "moral lesson"],
        is_suitable_for_long_form=False,
        open_endedness_score=0.0
    )
    logger.log_narrative_plan(plan)
    assert "narrative_plan" in logger.current_session
    print("    [OK] Narrative plan logged")

    # Test 3: Log generation
    print("  Testing log_generation...")
    evaluation = JudgeEvaluation(
        overall_score=8.5,
        age_appropriate=True,
        feedback="Great story!",
        strengths=["engaging", "age-appropriate"],
        improvements_needed=[],
        needs_revision=False
    )
    logger.log_generation(
        generation_type="initial",
        content="Once upon a time, there was a bunny...",
        evaluation=evaluation,
        revision_count=0
    )
    assert len(logger.current_session["generations"]) == 1
    print("    [OK] Generation logged")

    # Test 4: Log user exit feedback
    print("  Testing log_user_exit_feedback...")
    logger.log_user_exit_feedback(
        feedback="This story was great but could use more details",
        story_content="Once upon a time, there was a bunny..."
    )
    assert logger.current_session["user_feedback"] is not None
    assert logger.current_session["user_feedback"]["feedback"] == "This story was great but could use more details"
    print("    [OK] Exit feedback logged")

    # Test 5: Verify file was created
    print("  Testing file creation...")
    assert os.path.exists(logger.session_file)
    with open(logger.session_file, 'r') as f:
        saved_data = json.load(f)
        assert saved_data["user_request"] == "A bunny who learns to share"
        assert "narrative_plan" in saved_data
        assert len(saved_data["generations"]) == 1
        assert saved_data["user_feedback"] is not None
    print("    [OK] Session file created and valid")

    # Test 6: Get historical feedback
    print("  Testing get_historical_feedback...")
    historical = logger.get_historical_feedback()
    assert len(historical) == 1
    assert historical[0]["feedback"] == "This story was great but could use more details"
    print("    [OK] Historical feedback retrieved")

    # Cleanup
    shutil.rmtree(test_dir)
    print("[OK] All FeedbackLogger tests passed!\n")

def test_json_structure():
    """Test the structure of saved JSON files"""
    print("[Testing JSON structure]")

    test_dir = "test_feedback_logs"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    logger = FeedbackLogger(log_dir=test_dir)
    logger.start_session("Test story request", "long")

    plan = NarrativePlan(
        story_category="fantasy",
        story_arc="quest",
        themes=["courage", "friendship"],
        target_length="long",
        complexity_level="age 7-10",
        key_elements=["magic", "adventure"],
        is_suitable_for_long_form=True,
        open_endedness_score=8.0
    )
    logger.log_narrative_plan(plan)

    # Log multiple generations
    for i in range(3):
        eval = JudgeEvaluation(
            overall_score=7.0 + i,
            age_appropriate=True,
            feedback=f"Chapter {i+1} feedback",
            strengths=["good pacing"],
            improvements_needed=["more detail"] if i == 0 else [],
            needs_revision=i == 0,
            open_endedness_score=8.0
        )
        logger.log_generation(
            generation_type="chapter",
            content=f"Chapter {i+1} content...",
            evaluation=eval,
            chapter_num=i+1,
            user_feedback_input=f"Make chapter {i+1} exciting" if i == 1 else None
        )

    # Verify JSON structure
    with open(logger.session_file, 'r') as f:
        data = json.load(f)

        # Check top-level keys
        assert "session_id" in data
        assert "timestamp" in data
        assert "user_request" in data
        assert "story_type" in data
        assert "narrative_plan" in data
        assert "generations" in data
        assert "user_feedback" in data

        # Check narrative plan structure
        assert "story_category" in data["narrative_plan"]
        assert "themes" in data["narrative_plan"]
        assert data["narrative_plan"]["target_length"] == "long"

        # Check generations structure
        assert len(data["generations"]) == 3
        for gen in data["generations"]:
            assert "timestamp" in gen
            assert "type" in gen
            assert "content" in gen
            assert "evaluation" in gen
            assert "chapter_number" in gen

            # Check evaluation structure
            assert "overall_score" in gen["evaluation"]
            assert "age_appropriate" in gen["evaluation"]
            assert "feedback" in gen["evaluation"]
            assert "strengths" in gen["evaluation"]
            assert "improvements_needed" in gen["evaluation"]

        print("  [OK] JSON structure is valid")
        print(f"  Session ID: {data['session_id']}")
        print(f"  Story type: {data['story_type']}")
        print(f"  Generations logged: {len(data['generations'])}")

    # Cleanup
    shutil.rmtree(test_dir)
    print("[OK] JSON structure test passed!\n")

def main():
    print("\n=== FEEDBACK LOGGING SYSTEM TESTS ===\n")

    try:
        test_feedback_logger()
        test_json_structure()
        print("="*40)
        print("ALL TESTS PASSED")
        print("="*40)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
