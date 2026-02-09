# Valentine Card Generator Skill

Generate personalized interactive scratch-off Valentine cards that can be shared via URL.

## Quick Usage

```bash
# Generate a card with defaults
python3 ~/.openclaw/workspace/skills/valentine-card/generate.py "Sarah"

# Full customization
python3 ~/.openclaw/workspace/skills/valentine-card/generate.py "Jordan" \
  --message "Dinner at 7pm?" \
  --time "7:00 PM" \
  --theme pink \
  --output ~/Desktop/jordan-valentine.html
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `name` | Required | Recipient's name (used in title) |
| `--message` | "Will you be my Valentine?" | Hidden message revealed by scratching |
| `--time` | "2pm" | Time shown after reveal |
| `--theme` | "pink" | Color theme: pink, red, purple, blue, gold |
| `--output` | `./valentine-{name}.html` | Output file path |
| `--hint` | "Scratch to reveal your message 💖" | Hint text below card |

## Themes

- **pink** — Classic romantic pink gradient
- **red** — Bold passionate red
- **purple** — Elegant purple/violet
- **blue** — Cool romantic blue
- **gold** — Luxurious gold/champagne

## Deployment Options

### Option 1: Direct Share
The generated HTML file is self-contained. Share via:
- Email attachment
- AirDrop
- Any file sharing method

### Option 2: Cloudflare Pages (Free)
```bash
# Install wrangler if needed
npm install -g wrangler

# Deploy
cd ~/.openclaw/workspace/skills/valentine-card
wrangler pages deploy ./output --project-name valentine-{name}
```

### Option 3: GitHub Pages
1. Create a gist with the HTML content
2. Use rawcdn.githack.com to serve it

## Features

- **Scratch-off interaction** — Touch/mouse to reveal message
- **Floating hearts animation** — Celebration when revealed
- **Yes/No buttons** — With persistent "Are you sure?" on No
- **Mobile-friendly** — Works on phones and tablets
- **Self-contained** — Single HTML file, no dependencies

## Examples

```bash
# Romantic dinner invite
python3 generate.py "Alex" --message "Fancy dinner tonight?" --time "7:30 PM" --theme gold

# Casual hangout
python3 generate.py "Best Friend" --message "Movie marathon this weekend?" --theme purple

# Classic Valentine
python3 generate.py "My Love" --message "Be mine forever? 💕" --time "Always" --theme red
```

## Batch Generation

```bash
# Generate for multiple people
for person in "Jordan" "Alex" "Sam"; do
  python3 generate.py "$person" --output "./cards/${person}.html"
done
```
