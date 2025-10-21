# Multi-Agent Bedtime Story System - Block Diagram
# Using OpenAI Agents SDK

## System Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                  │
│              "What kind of story do you want to hear?"                   │
│                                                                          │
│              "Short story or long story?"                                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STORYTELLING ORCHESTRATOR                             │
│              (Coordinates all agents using OpenAI Agents SDK)            │
│                                                                          │
│                  Uses: agents.Agent & agents.Runner                      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                      ┌────────┴────────┐
                      │                 │
                   SHORT              LONG
                   STORY              STORY
                      │                 │
                      ▼                 ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │   SHORT STORY PATH    │       │   LONG STORY PATH     │
        └───────────┬───────────┘       └───────────┬───────────┘
                    │                               │
                    ▼                               ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │  NARRATIVE DIRECTOR AGENT    │ │  NARRATIVE DIRECTOR AGENT    │
        │  Temperature: 0.3            │ │  Temperature: 0.3            │
        ├──────────────────────────────┤ ├──────────────────────────────┤
        │  • Analyzes user request     │ │  • Analyzes user request     │
        │  • Categorizes story type    │ │  • Categorizes story type    │
        │  • Determines story arc      │ │  • Determines story arc      │
        │  • Selects themes            │ │  • Selects themes            │
        │  • Sets complexity level     │ │  • Sets complexity level     │
        │  • Defines key elements      │ │  • Defines key elements      │
        └──────────────┬───────────────┘ │  • Evaluates long-form fit   │
                       │                 │  • Scores open-endedness     │
                       │                 └──────────────┬───────────────┘
                       │                                │
                       │ NarrativePlan                  │ NarrativePlan
                       │ (target_length: "short")       │ (target_length: "long")
                       │                                │ + is_suitable_for_long_form
                       │                                │ + open_endedness_score
                       ▼                                ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │    STORYTELLER AGENT         │ │  CHAPTER GENERATION LOOP     │
        │    (Single Story Mode)       │ │  (max 20 chapters)           │
        │    Temperature: 0.8          │ │                              │
        └──────────────┬───────────────┘ └──────────────┬───────────────┘
                       │                                │
                       ▼                                ▼ for each chapter
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │    STORYTELLER AGENT         │ │    STORYTELLER AGENT         │
        │    Temperature: 0.8          │ │    (Chapter Mode)            │
        ├──────────────────────────────┤ │    Temperature: 0.8          │
        │  • Generates complete story  │ ├──────────────────────────────┤
        │  • 500-800 words             │ │  • Receives ChapterContext   │
        │  • Follows narrative plan    │ │    - Chapter number          │
        │  • Age-appropriate           │ │    - Previous chapters       │
        │  • Bedtime-suitable          │ │    - Narrative plan          │
        └──────────────┬───────────────┘ │  • Maintains continuity      │
                       │                 │  • Gentle cliffhanger ending │
                       │                 │  • 400-600 words/chapter     │
                       ▼                 └──────────────┬───────────────┘
                  Generated Story                       │
                       │                           Generated Chapter
                       ▼                                ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │       JUDGE AGENT            │ │       JUDGE AGENT            │
        │       Temperature: 0.1       │ │       (Chapter Mode)         │
        ├──────────────────────────────┤ │       Temperature: 0.1       │
        │  • Evaluates story quality   │ ├──────────────────────────────┤
        │  • Age-appropriateness       │ │  • Same as short story +     │
        │  • Story structure           │ │  • Open-endedness score      │
        │  • Engagement                │ │  • Continuity check          │
        │  • Theme integration         │ │  • Chapter ending quality    │
        │  • Bedtime suitability       │ │  • Future potential          │
        │  • Overall score (0-10)      │ │  • Overall score (0-10)      │
        └──────────────┬───────────────┘ └──────────────┬───────────────┘
                       │                                │
                       │ JudgeEvaluation                │ JudgeEvaluation
                       │                                │ + open_endedness_score
                       ▼                                ▼
        ┌──────────────┐                 ┌──────────────┐
        │  Decision:   │                 │  Decision:   │
        │  Needs       │                 │  Needs       │
        │  Revision?   │                 │  Revision?   │
        └──┬────────┬──┘                 └──┬────────┬──┘
           │        │                       │        │
        NO │        │ YES                NO │        │ YES (score < 7.0)
           │        │                       │        │
           │        ▼                       │        ▼
           │  ┌────────────────────┐        │  ┌────────────────────┐
           │  │ REVISION AGENT     │        │  │ REVISION AGENT     │
           │  │ Temperature: 0.7   │        │  │ Temperature: 0.7   │
           │  │                    │        │  │ (1 revision/chapter)│
           │  │ max 2 revisions    │        │  └─────────┬──────────┘
           │  └─────────┬──────────┘        │            │
           │            │                   │            ▼
           │            ▼                   │      Re-evaluate
           │      [Re-evaluate]             │            │
           │            │                   │            ▼
           ▼            ▼                   ▼       [Continue]
     [APPROVED]   [APPROVED]          [Display Chapter]
           │            │                   │
           ▼            ▼                   ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │      FINAL SHORT STORY       │ │   USER CONTINUATION PROMPT   │
        │                              │ │                              │
        │  • Quality approved          │ │  "Continue to Chapter N?"    │
        │  • Age-appropriate           │ │                              │
        │  • Engaging narrative        │ │  YES → Generate next chapter │
        │  • Follows story arc         │ │  NO  → End story             │
        │  • Bedtime-suitable          │ │                              │
        └──────────────┬───────────────┘ │  Max 20 chapters             │
                       │                 └──────────────┬───────────────┘
                       ▼                                │
┌──────────────────────────────────────┐                │
│   OUTPUT TO USER (SHORT STORY)       │                │ (Loops back to
│                                      │                │  Chapter Generation)
│  • Complete story                    │                │
│  • Quality Score (0-10)              │                ▼
│  • Number of revisions               │ ┌──────────────────────────────────┐
│  • Age-appropriate badge             │ │  OUTPUT TO USER (LONG STORY)     │
└──────────────────────────────────────┘ │                                  │
                                         │  • Chapter-by-chapter display    │
                                         │  • Quality & open-endedness      │
                                         │    scores per chapter            │
                                         │  • Interactive continuation      │
                                         │  • Total chapters generated      │
                                         └──────────────────────────────────┘
```

## Agent Details (OpenAI Agents SDK Implementation)

All agents are implemented using the OpenAI Agents SDK (`agents.Agent` and `agents.Runner`).

### 1. Narrative Director Agent
- **Purpose**: Strategic planning and story architecture + long-form evaluation
- **Input**: Raw user request + target_length ("short" or "long")
- **Output**: Structured NarrativePlan object (JSON format)
- **Temperature**: 0.3 (balanced - needs creativity but consistency)
- **SDK Usage**: `Agent(name="NarrativeDirector", instructions=..., model="gpt-3.5-turbo", temperature=0.3)`
- **Key Responsibilities**:
  - Story categorization (adventure, friendship, magical, etc.)
  - Story arc selection (Hero's Journey, Overcoming Challenge, etc.)
  - Theme identification
  - Complexity calibration for ages 5-10
  - **NEW**: Evaluate long-form suitability (can concept sustain 20 chapters?)
  - **NEW**: Score open-endedness potential (0-10)

### 2. Storyteller Agent
- **Purpose**: Creative content generation (short stories + chapters)
- **Input**:
  - Short story mode: User request + NarrativePlan
  - Chapter mode: User request + NarrativePlan + ChapterContext
- **Output**: Complete bedtime story (500-800 words) OR chapter (400-600 words)
- **Temperature**: 0.8 (high - maximize creativity)
- **SDK Usage**: `Agent(name="Storyteller", instructions=..., model="gpt-3.5-turbo", temperature=0.8)`
- **Key Responsibilities**:
  - Generate engaging narrative
  - Follow story structure
  - Use age-appropriate language
  - Create imaginative content
  - Ensure bedtime suitability
  - **NEW (Chapter mode)**: Maintain continuity across chapters
  - **NEW (Chapter mode)**: Create gentle cliffhangers (curiosity, not anxiety)
  - **NEW (Chapter mode)**: Track previous chapters for consistency

### 3. Judge Agent
- **Purpose**: Quality assurance and evaluation
- **Input**: Story/Chapter + user request + narrative plan + is_chapter flag
- **Output**: JudgeEvaluation object with scores and feedback (JSON format)
- **Temperature**: 0.1 (very low - needs consistency in evaluation)
- **SDK Usage**: `Agent(name="Judge", instructions=..., model="gpt-3.5-turbo", temperature=0.1)`
- **Evaluation Criteria (All Stories)**:
  1. Age-appropriateness (5-10 years) - CRITICAL
  2. Story structure quality
  3. Engagement level
  4. Theme incorporation
  5. Language quality
  6. Bedtime suitability
  7. Overall quality score (0-10)
- **Additional Criteria (Long-form Chapters)**:
  8. **Open-endedness (0-10)**: Sets up future possibilities?
  9. **Continuity**: Maintains consistency with previous chapters?
  10. **Chapter ending**: Provides closure while inviting continuation?
- **Decision Logic**:
  - Short stories: Score ≥ 8.0 + age_appropriate = approved
  - Chapters: Score ≥ 7.0 (lighter threshold to maintain flow)
  - Long-form: open_endedness_score ≥ 7.0 for concept approval

### 4. Revision Agent
- **Purpose**: Iterative improvement based on feedback
- **Input**: Original story/chapter + judge evaluation + narrative plan
- **Output**: Improved story/chapter
- **Temperature**: 0.7 (moderate-high - needs creativity within constraints)
- **SDK Usage**: `Agent(name="RevisionAgent", instructions=..., model="gpt-3.5-turbo", temperature=0.7)`
- **Iteration Limits**:
  - Short stories: max 2 revisions
  - Chapters: max 1 revision (to maintain flow and pacing)
- **Key Responsibilities**:
  - Address specific judge feedback
  - Maintain story strengths
  - Fix identified issues
  - Preserve narrative essence
  - Re-submit for evaluation

## Data Structures (Python Dataclasses)

### NarrativePlan
```python
@dataclass
class NarrativePlan:
    story_category: str                    # e.g., "adventure", "friendship"
    story_arc: str                         # e.g., "Hero's Journey"
    themes: List[str]                      # e.g., ["bravery", "kindness"]
    target_length: str                     # "short" or "long"
    complexity_level: str                  # age-appropriate description
    key_elements: List[str]                # must-include story elements
    is_suitable_for_long_form: bool = False  # NEW: Can sustain 20 chapters?
    open_endedness_score: float = 0.0      # NEW: Long-form potential (0-10)
```

### JudgeEvaluation
```python
@dataclass
class JudgeEvaluation:
    overall_score: float                   # 0.0 to 10.0
    age_appropriate: bool                  # safety check
    feedback: str                          # detailed evaluation
    strengths: List[str]                   # what works well
    improvements_needed: List[str]         # what needs fixing
    needs_revision: bool                   # revision decision
    open_endedness_score: Optional[float] = None  # NEW: For long-form chapters
```

### ChapterContext (NEW)
```python
@dataclass
class ChapterContext:
    chapter_number: int                    # Current chapter being generated
    previous_chapters: List[str]           # All previous chapter texts
    narrative_plan: NarrativePlan          # Overall story plan
    user_request: str                      # Original user request
```

## Quality Control Features

1. **Multi-Agent Specialization**: Each agent has a specific role and temperature setting
2. **OpenAI Agents SDK**: Production-ready framework using `agents.Agent` and `agents.Runner`
3. **Structured Communication**: Agents pass structured data objects (dataclasses), not just text
4. **Iterative Refinement**: Judge-Revision loop (max 2 for short stories, max 1 for chapters)
5. **Graceful Degradation**: Fallback plans if JSON parsing fails
6. **Transparent Process**: Verbose mode shows each agent's work
7. **Metadata Tracking**: Returns revision count and quality scores
8. **NEW - Interactive Flow**: User controls chapter-by-chapter progression
9. **NEW - Open-endedness Scoring**: Evaluates long-form storytelling potential
10. **NEW - Chapter Continuity**: Maintains character and plot consistency across 20 chapters

## Temperature Strategy

| Agent               | Temperature | Rationale                                      |
|---------------------|-------------|------------------------------------------------|
| Narrative Director  | 0.3         | Balance planning consistency with creativity   |
| Storyteller         | 0.8         | Maximum creativity for engaging narratives     |
| Judge               | 0.1         | Consistent, objective evaluation               |
| Revision Agent      | 0.7         | Creative improvements within constraints       |

All agents use `gpt-3.5-turbo` model as required by the assignment.

## Agentic Best Practices Applied

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Specialization**: Agents are optimized for their specific tasks (via temperature)
3. **Structured Communication**: Use of dataclasses for type-safe agent communication
4. **Chain of Thought**: Narrative plan → Story/Chapter → Evaluation → Revision
5. **Self-Correction**: Judge provides feedback, Revision agent improves
6. **Orchestration Layer**: `StoryOrchestrator` class manages all agent interactions
7. **Modularity**: Each agent can be tested/improved independently
8. **Fail-Safe Mechanisms**: Fallback logic for JSON parsing errors
9. **Iteration Limits**: Prevents infinite revision loops (2 for stories, 1 for chapters)
10. **Observability**: Verbose mode for understanding agent decisions
11. **OpenAI Agents SDK**: Uses official production-ready framework for agent workflows
12. **Stateful Context**: ChapterContext maintains narrative continuity across chapters
13. **Human-in-the-Loop**: User controls story progression after each chapter
14. **Adaptive Evaluation**: Different scoring thresholds for short vs. long-form content

## Key Implementation Features

### Short Story Mode
- Single complete story (500-800 words)
- Judge-Revision loop with strict quality threshold (≥8.0)
- Maximum 2 revisions for quality
- Complete narrative arc with resolution

### Long Story Mode (NEW)
- Multi-chapter generation (up to 20 chapters)
- Open-endedness evaluation before starting
- Chapter-by-chapter user control ("Continue to Chapter N?")
- Lighter revision requirements (threshold ≥7.0, max 1 revision/chapter)
- Maintains narrative continuity via ChapterContext
- Each chapter 400-600 words with gentle cliffhangers
- Displays quality and open-endedness scores per chapter

## Technology Stack
- **Framework**: OpenAI Agents SDK (`openai-agents>=0.4.0`)
- **LLM**: OpenAI GPT-3.5-turbo
- **Language**: Python 3.12+
- **Agent Pattern**: Multi-agent orchestration with specialized roles
- **Execution**: Synchronous via `agents.Runner.run_sync()`
