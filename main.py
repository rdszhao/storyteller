"""
Bedtime Story Generator - Multi-Agent System using OpenAI Agents SDK

Before submitting the assignment, describe here in a few sentences what you would
have built next if you spent 2 more hours on this project:

If I had 2 more hours:
1. Add persistent story state management to allow resuming multi-chapter stories across sessions
2. Implement dynamic story branching where users can provide feedback/choices that influence the next chapter
3. Add visual storytelling elements (ASCII art or image generation) for key moments
4. Create a more sophisticated narrative memory system that tracks character development and plot threads across chapters
5. Add voice narration capabilities using OpenAI's TTS API for a true bedtime story experience
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import inquirer
from dotenv import load_dotenv
from bedtime_story_generator.core.orchestrator import StoryOrchestrator
from bedtime_story_generator.utils.feedback_logger import FeedbackLogger

load_dotenv()


def main():
    """Run the bedtime story generator CLI application."""
    print("\nBEDTIME STORY GENERATOR\n")
    logger = FeedbackLogger()
    orchestrator = StoryOrchestrator(feedback_logger=logger)

    user_request = input('What kind of story do you want to hear?\n').strip()
    if not user_request:
        print("No story request provided. Goodbye!")
        return

    questions = [
        inquirer.List(
                    'length',
                    message="Choose story length",
                    choices=[
                        'Short story (complete in one telling)',
                        'Long story (multiple chapters, up to 20)'
                    ],
                    carousel=True
                )
    ]
    answers = inquirer.prompt(questions)

    if not answers:
        print('Goodbye!')
        return

    if answers['length'].startswith('Short'):
        # Short story mode
        logger.start_session(user_request, "short")
        story, evaluation, _revision_count = orchestrator.create_short_story(user_request)

        while True:
            print('\n' + '='*60 + '\n')
            print(story)
            print('\n' + '='*60 + '\n')

            # Ask if user wants to revise
            revision_questions = [
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=[
                        'This is perfect, finish here',
                        'Request a revision with feedback',
                        'Exit and provide feedback'
                    ],
                    carousel=True
                )
            ]
            revision_answer = inquirer.prompt(revision_questions)

            if not revision_answer:
                break

            if revision_answer['action'].startswith('This is perfect'):
                break
            elif revision_answer['action'].startswith('Exit and provide'):
                # Get exit feedback
                exit_feedback = input('\nWhat feedback would you like to provide about this story? ').strip()
                if exit_feedback:
                    logger.log_user_exit_feedback(exit_feedback, story)
                    print("\nThank you for your feedback! It will help improve future stories.")
                break
            else:
                # Get user feedback for revision
                feedback = input('\nWhat would you like changed or improved? ').strip()
                if feedback:
                    story = orchestrator.revise_chapter_with_feedback(
                        story, user_request,
                        orchestrator.create_narrative_plan(user_request, "short"),
                        feedback
                    )
                else:
                    break
    else:
        # Long story mode
        logger.start_session(user_request, "long")
        narrative_plan = orchestrator.init_long_story(user_request)
        chapters = []
        max_chapters = 20
        next_chapter_feedback = None

        for chapter_num in range(1, max_chapters + 1):
            chapter, _evaluation = orchestrator.generate_next_chapter(
                user_request, narrative_plan, chapters, chapter_num, next_chapter_feedback
            )
            next_chapter_feedback = None  # Clear feedback after use

            # Chapter revision loop
            while True:
                print(f"\n{'='*60}")
                print(f"CHAPTER {chapter_num}")
                print(f"{'='*60}\n")
                print(chapter)
                print(f"\n{'='*60}\n")

                if chapter_num < max_chapters:
                    chapter_questions = [
                        inquirer.List(
                            'action',
                            message="What would you like to do?",
                            choices=[
                                'Continue to next chapter',
                                'Revise this chapter',
                                'Add feedback for next chapter',
                                'End story here',
                                'Exit and provide feedback'
                            ],
                            carousel=True
                        )
                    ]
                else:
                    chapter_questions = [
                        inquirer.List(
                            'action',
                            message="Final chapter - what would you like to do?",
                            choices=[
                                'Story is complete',
                                'Revise this chapter',
                                'Exit and provide feedback'
                            ],
                            carousel=True
                        )
                    ]

                chapter_answer = inquirer.prompt(chapter_questions)

                if not chapter_answer:
                    chapters.append(chapter)
                    return

                action = chapter_answer['action']

                if action == 'Continue to next chapter' or action == 'Story is complete':
                    chapters.append(chapter)
                    break
                elif action == 'End story here':
                    chapters.append(chapter)
                    return
                elif action == 'Exit and provide feedback':
                    chapters.append(chapter)
                    # Get exit feedback
                    full_story = '\n\n'.join([f"CHAPTER {i+1}\n\n{ch}" for i, ch in enumerate(chapters)])
                    exit_feedback = input('\nWhat feedback would you like to provide about this story? ').strip()
                    if exit_feedback:
                        logger.log_user_exit_feedback(exit_feedback, full_story)
                        print("\nThank you for your feedback! It will help improve future stories.")
                    return
                elif action == 'Revise this chapter':
                    feedback = input('\nWhat would you like changed in this chapter? ').strip()
                    if feedback:
                        chapter = orchestrator.revise_chapter_with_feedback(
                            chapter, user_request, narrative_plan, feedback, chapter_num
                        )
                    # Loop continues to show revised chapter
                elif action == 'Add feedback for next chapter':
                    next_chapter_feedback = input('\nWhat should the next chapter include or focus on? ').strip()
                    if next_chapter_feedback:
                        print(f"\nFeedback noted for Chapter {chapter_num + 1}")
                    chapters.append(chapter)
                    break

            if chapter_num >= max_chapters:
                print(f"\nYou've reached the maximum of {max_chapters} chapters!")
                break


if __name__ == "__main__":
    main()
