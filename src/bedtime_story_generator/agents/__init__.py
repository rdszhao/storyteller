'''Agent definitions for the bedtime story system.'''

from bedtime_story_generator.agents.narrative_director import narrative_director
from bedtime_story_generator.agents.storyteller import storyteller
from bedtime_story_generator.agents.judge import judge
from bedtime_story_generator.agents.revision import revision_agent

__all__ = ['narrative_director', 'storyteller', 'judge', 'revision_agent']
