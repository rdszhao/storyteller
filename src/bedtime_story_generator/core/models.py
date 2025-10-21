'''Data models for the bedtime story system.'''

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NarrativePlan:
    '''Structured plan for story generation'''
    story_category: str
    story_arc: str
    themes: List[str]
    target_length: str
    complexity_level: str
    key_elements: List[str]
    is_suitable_for_long_form: bool = False
    open_endedness_score: float = 0.0


@dataclass
class JudgeEvaluation:
    '''Evaluation results from the judge agent'''
    overall_score: float
    age_appropriate: bool
    feedback: str
    strengths: List[str]
    improvements_needed: List[str]
    needs_revision: bool
    open_endedness_score: Optional[float] = None


@dataclass
class ChapterContext:
    '''Context for chapter generation'''
    chapter_number: int
    previous_chapters: List[str]
    narrative_plan: NarrativePlan
    user_request: str