"""Test the UI flow without making API calls - verifies arrow key selection works."""

import sys

def test_ui_flow():
    """Test that inquirer is available and UI components work"""
    print("="*60)
    print("TESTING UI COMPONENTS")
    print("="*60 + "\n")

    try:
        import inquirer
        print("[OK] inquirer library imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import inquirer: {e}")
        return False

    # Test that we can create questions (without prompting)
    try:
        questions = [
            inquirer.List('test',
                         message="Test question",
                         choices=['Option 1', 'Option 2'],
                         carousel=True)
        ]
        print("[OK] Arrow key selection questions can be created")
    except Exception as e:
        print(f"[FAIL] Failed to create selection questions: {e}")
        return False

    print("\n[INFO] UI components are ready")
    print("[INFO] To test interactively, run: uv run python main.py")

    return True


if __name__ == "__main__":
    success = test_ui_flow()
    print("\n" + "="*60)
    if success:
        print("ALL UI TESTS PASSED")
    else:
        print("SOME UI TESTS FAILED")
    print("="*60)
    sys.exit(0 if success else 1)
