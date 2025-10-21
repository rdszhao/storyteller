# Usage Guide

## Running the Application

```bash
uv run python main.py
```

## User Flow

### 1. Story Request (Text Input)
```
What kind of story do you want to hear?
```
Enter your story idea, for example:
- "A bunny who learns to share"
- "A brave knight who saves a dragon"
- "A girl who discovers magic in her garden"

### 2. Story Length (Arrow Key Selection)
```
Choose story length
> Short story (complete in one telling)
  Long story (multiple chapters, up to 20)
```

Use arrow keys (↑/↓) to select, press Enter to confirm.

### 3. Story Generation

While the story is being generated, you'll see a spinner:

```
⠋ Generating your story...
```

The spinner animates to show progress. If the story needs improvement, it updates:

```
⠋ Improving story (revision 1)...
```

When complete:

```
✔ Story ready!
```

### 4. Story Appears

**You see:**
```
============================================================

[Your story text appears here]

============================================================
```

**You don't see:**
- Agent processing details
- Quality scores
- Metrics
- Evaluation results

### 5. Interactive Options

#### For Short Stories:

After the story appears, you can:
```
What would you like to do?
> This is perfect, finish here
  Request a revision with feedback
```

If you request a revision, provide text feedback and the story will be regenerated.

#### For Long Stories:

After each chapter, you can:
```
What would you like to do?
> Continue to next chapter
  Revise this chapter
  Add feedback for next chapter
  End story here
```

**Options:**
- **Continue**: Move to next chapter
- **Revise this chapter**: Provide feedback to improve current chapter
- **Add feedback for next chapter**: Guide what happens in the upcoming chapter
- **End story here**: Stop generating more chapters

You can revise any chapter multiple times until you're satisfied.

## Features

- **Clean Output**: Just the story text, nothing else
- **Plain Text Stories**: No emojis, no special formatting
- **Arrow Key Navigation**: All choices after initial input use arrow keys
- **Silent Processing**: Multi-agent quality control happens behind the scenes
- **Interactive Chapters**: Control how long your story continues
- **Age-Appropriate**: All stories suitable for ages 5-10

## Testing

Run tests without making API calls:
```bash
# Test structure and imports
uv run python test_setup.py

# Test UI components
uv run python test_ui.py
```

Run full API test (requires OPENAI_API_KEY):
```bash
uv run python test_api.py
```

## Configuration

Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_key_here
```
