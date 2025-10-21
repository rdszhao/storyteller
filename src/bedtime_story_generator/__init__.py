"""
Bedtime Story Generator - Multi-Agent AI System

A production-ready bedtime story generator using OpenAI's Agents SDK
with specialized agents for narrative planning, storytelling, quality
evaluation, and revision.
"""

__version__ = "1.0.0"

from bedtime_story_generator.core.models import (
    NarrativePlan,
    JudgeEvaluation,
    ChapterContext
)
from bedtime_story_generator.core.orchestrator import StoryOrchestrator
from bedtime_story_generator.utils.feedback_logger import FeedbackLogger

__all__ = [
    "NarrativePlan",
    "JudgeEvaluation",
    "ChapterContext",
    "StoryOrchestrator",
    "FeedbackLogger",
]
