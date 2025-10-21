"""Story Orchestrator - Coordinates multi-agent storytelling workflow."""

import json
from typing import List, Optional, Tuple
from halo import Halo
from agents import Runner

from bedtime_story_generator.agents import narrative_director, storyteller, judge, revision_agent
from bedtime_story_generator.core.models import NarrativePlan, JudgeEvaluation, ChapterContext
from bedtime_story_generator.utils.feedback_logger import FeedbackLogger

class StoryOrchestrator:
    '''Orchestrates the multi-agent storytelling system'''

    def __init__(self, show_spinner: bool = True, feedback_logger: Optional[FeedbackLogger] = None):
        self.show_spinner = show_spinner
        self.max_revisions = 2
        self.logger = feedback_logger or FeedbackLogger()

    def _parse_json_response(self, response: str, fallback: dict) -> dict:
        '''Safely parse JSON response with fallback'''
        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return fallback

    def create_narrative_plan(self, user_request: str, target_length: str) -> NarrativePlan:
        """Create narrative plan using the Narrative Director agent"""
        prompt = f"""
        Analyze this story request and create a narrative plan.

        User request: {user_request}
        Target length: {target_length}

        Provide your analysis in JSON format.
        """

        result = Runner.run_sync(narrative_director, prompt)
        response = result.final_output

        parsed = self._parse_json_response(response, {
            'story_category': 'general',
            'story_arc': 'simple journey',
            'themes': ['friendship', 'courage'],
            'target_length': target_length,
            'complexity_level': 'age 5-10',
            'key_elements': ['character growth'],
            'is_suitable_for_long_form': target_length == 'long',
            'open_endedness_score': 7.0 if target_length == 'long' else 0.0
        })

        narrative_plan = NarrativePlan(**{k: v for k, v in parsed.items() if k in NarrativePlan.__annotations__})
        self.logger.log_narrative_plan(narrative_plan)
        return narrative_plan

    def generate_story(
            self,
            user_request: str,
            narrative_plan: NarrativePlan,
            chapter_context: Optional[ChapterContext] = None,
            user_feedback: Optional[str] = None
        ) -> str:
        '''Generate story using the Storyteller agent'''
        if chapter_context:
            previous_summary = ""
            if chapter_context.previous_chapters:
                previous_summary = '\n\nPrevious chapters summary:\n' + '\n'.join([f'Chapter {i+1}: {ch[:200]}...' for i, ch in enumerate(chapter_context.previous_chapters)])

            user_feedback_section = ''
            if user_feedback:
                user_feedback_section = f"\n\nUser feedback for this chapter:\n{user_feedback}"

            prompt = f"""
            Write Chapter {chapter_context.chapter_number} of a bedtime story.

            User's original request: {user_request}
            Story category: {narrative_plan.story_category}
            Story arc: {narrative_plan.story_arc}
            Themes: {', '.join(narrative_plan.themes)}
            Key elements: {', '.join(narrative_plan.key_elements)}
            {previous_summary}
            {user_feedback_section}

            Requirements:
            - Continue the narrative naturally from previous chapters
            - Maintain character consistency
            - Include a gentle chapter-ending hook
            - Keep it age-appropriate and bedtime-suitable
            - Plain text only - no bold, italics, or special formatting
            - No emojis
            - 400-600 words"""
        else:
            prompt = f"""
            Write a complete bedtime story based on this request.

            User request: {user_request}
            Story category: {narrative_plan.story_category}
            Story arc: {narrative_plan.story_arc}
            Themes: {', '.join(narrative_plan.themes)}
            Key elements: {', '.join(narrative_plan.key_elements)}
            Complexity: {narrative_plan.complexity_level}

            Requirements:
            - Complete story with beginning, middle, and end
            - Age-appropriate for 5-10 year olds
            - Bedtime-suitable (calming, positive)
            - Plain text only - no bold, italics, or special formatting
            - No emojis
            - 500-800 words
            """

        result = Runner.run_sync(storyteller, prompt)
        story = result.final_output

        return story

    def evaluate_story(
            self,
            story: str,
            user_request: str,
            narrative_plan: NarrativePlan,
            is_chapter: bool = False
        ) -> JudgeEvaluation:
        '''Evaluate story using the Judge agent'''
        story_type = 'chapter' if is_chapter else 'complete story'
        long_form_note = ''
        if narrative_plan.target_length == 'long':
            long_form_note = '\nThis is a LONG-FORM story. Evaluate open-endedness and chapter continuation potential.'

        prompt = f"""
        Evaluate this {story_type} for quality and appropriateness.

        User request: {user_request}
        Narrative plan themes: {', '.join(narrative_plan.themes)}
        {long_form_note}

        Story to evaluate:
        {story}

        Provide your evaluation in JSON format.
        """

        result = Runner.run_sync(judge, prompt)
        response = result.final_output

        parsed = self._parse_json_response(response, {
            'overall_score': 7.5,
            'age_appropriate': True,
            'feedback': 'Story meets basic requirements',
            'strengths': ['age-appropriate'],
            'improvements_needed': [],
            'needs_revision': False,
            'open_endedness_score': 7.0 if narrative_plan.target_length == 'long' else None
        })

        return JudgeEvaluation(**{k: v for k, v in parsed.items() if k in JudgeEvaluation.__annotations__})

    def revise_story(self, original_story: str, evaluation: JudgeEvaluation,
                    user_request: str, narrative_plan: NarrativePlan,
                    user_feedback: Optional[str] = None) -> str:
        '''Revise story using the Revision Agent'''
        user_feedback_section = ""
        if user_feedback:
            user_feedback_section = f"\n\nUser's specific feedback:\n{user_feedback}"

        prompt = f"""
        Revise this story based on the feedback.

        Original user request: {user_request}
        Themes: {', '.join(narrative_plan.themes)}

        Original story:
        {original_story}

        Judge's feedback:
        - Overall score: {evaluation.overall_score}/10
        - Strengths: {', '.join(evaluation.strengths)}
        - Improvements needed: {', '.join(evaluation.improvements_needed)}
        - Detailed feedback: {evaluation.feedback}
        {user_feedback_section}

        Revise the story to address the improvements while maintaining its strengths.
        """

        result = Runner.run_sync(revision_agent, prompt)
        revised_story = result.final_output

        return revised_story

    def create_short_story(self, user_request: str) -> Tuple[str, JudgeEvaluation, int]:
        '''Create a short story with quality assurance loop'''
        spinner = Halo(text='Generating your story...', spinner='dots') if self.show_spinner else None

        if spinner:
            spinner.start()

        try:
            narrative_plan = self.create_narrative_plan(user_request, 'short')
            story = self.generate_story(user_request, narrative_plan)
            revision_count = 0
            while revision_count < self.max_revisions:
                evaluation = self.evaluate_story(story, user_request, narrative_plan)
                self.logger.log_generation(
                    generation_type='initial' if revision_count == 0 else 'revision',
                    content=story,
                    evaluation=evaluation,
                    revision_count=revision_count
                )
                if not evaluation.needs_revision:
                    break
                if spinner:
                    spinner.text = f"Improving story (revision {revision_count + 1})..."

                story = self.revise_story(story, evaluation, user_request, narrative_plan)
                revision_count += 1

            final_evaluation = self.evaluate_story(story, user_request, narrative_plan)

            self.logger.log_generation(
                generation_type='final',
                content=story,
                evaluation=final_evaluation,
                revision_count=revision_count
            )

            if spinner:
                spinner.succeed('Story ready!')

            return story, final_evaluation, revision_count

        except Exception as e:
            if spinner:
                spinner.fail('Story generation failed')
            raise

    def init_long_story(self, user_request: str) -> NarrativePlan:
        '''Initialize a long story and return the narrative plan'''
        narrative_plan = self.create_narrative_plan(user_request, 'long')
        return narrative_plan

    def generate_next_chapter(
            self,
            user_request: str,
            narrative_plan: NarrativePlan,
            chapters: List[str],
            chapter_num: int,
            user_feedback: Optional[str] = None
        ) -> Tuple[str, JudgeEvaluation]:
        '''Generate the next chapter in a long story'''
        spinner = Halo(text=f'Writing Chapter {chapter_num}...', spinner='dots') if self.show_spinner else None

        if spinner:
            spinner.start()

        try:
            chapter_context = ChapterContext(
                chapter_number=chapter_num,
                previous_chapters=chapters,
                narrative_plan=narrative_plan,
                user_request=user_request
            )
            chapter = self.generate_story(user_request, narrative_plan, chapter_context, user_feedback)
            evaluation = self.evaluate_story(chapter, user_request, narrative_plan, is_chapter=True)

            self.logger.log_generation(
                generation_type="chapter",
                content=chapter,
                evaluation=evaluation,
                chapter_num=chapter_num,
                user_feedback_input=user_feedback
            )

            if evaluation.needs_revision and evaluation.overall_score < 7.0:
                if spinner:
                    spinner.text = f'Refining Chapter {chapter_num}...'

                chapter = self.revise_story(chapter, evaluation, user_request, narrative_plan)
                evaluation = self.evaluate_story(chapter, user_request, narrative_plan, is_chapter=True)

                self.logger.log_generation(
                    generation_type='revision',
                    content=chapter,
                    evaluation=evaluation,
                    chapter_num=chapter_num,
                    revision_count=1
                )

            if spinner:
                spinner.succeed(f"Chapter {chapter_num} ready!")

            return chapter, evaluation

        except Exception as e:
            if spinner:
                spinner.fail(f"Chapter {chapter_num} generation failed")
            raise

    def revise_chapter_with_feedback(self, chapter: str, user_request: str,
                                    narrative_plan: NarrativePlan, user_feedback: str,
                                    chapter_num: Optional[int] = None) -> str:
        '''Revise a chapter based on user feedback'''
        spinner = Halo(text='Revising based on your feedback...', spinner='dots') if self.show_spinner else None

        if spinner:
            spinner.start()

        try:
            evaluation = self.evaluate_story(chapter, user_request, narrative_plan, is_chapter=True)
            revised_chapter = self.revise_story(chapter, evaluation, user_request, narrative_plan, user_feedback)
            final_evaluation = self.evaluate_story(revised_chapter, user_request, narrative_plan, is_chapter=True)

            self.logger.log_generation(
                generation_type='user_revision',
                content=revised_chapter,
                evaluation=final_evaluation,
                user_feedback_input=user_feedback,
                chapter_num=chapter_num
            )

            if spinner:
                spinner.succeed('Revision complete!')

            return revised_chapter

        except Exception as e:
            if spinner:
                spinner.fail('Revision failed')
            raise