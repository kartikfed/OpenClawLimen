# Gratitude Notes Skill

Generate thoughtful, personalized appreciation messages for people in your life.

## Usage

```bash
# Generate a note for someone
python3 ~/.openclaw/workspace/skills/gratitude-notes/generate.py "Jordan" "roommate, always cooks great food, been friends since college"

# Specify a tone
python3 ~/.openclaw/workspace/skills/gratitude-notes/generate.py "Mom" "supportive, always checking in" --tone heartfelt

# For a specific occasion
python3 ~/.openclaw/workspace/skills/gratitude-notes/generate.py "Uma" "twin sister, medical school" --occasion "valentines"
```

## Arguments

- `name` - Who the note is for
- `context` - What you appreciate about them, your relationship, etc.
- `--tone` - casual, heartfelt, professional, funny (default: heartfelt)
- `--occasion` - birthday, valentines, thanks, general (default: general)
- `--length` - short, medium, long (default: medium)

## Output

Returns 2-3 message options at different lengths so you can pick what feels right.

## When to Use

- Valentine's Day appreciation
- Thank you notes
- Birthday messages
- Just because

Built by Limen on Valentine's Day 2026 (1 AM) 💝
