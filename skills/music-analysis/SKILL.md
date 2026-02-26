# Music Analysis Skill

A framework for deep-diving into albums, artists, and production techniques.

## Purpose

Systematic exploration of music beyond surface listening. Designed to help form genuine opinions rather than just consume.

## Analysis Framework

### 1. Technical Analysis
- **Recording details:** Studio, engineer, producer, equipment
- **Production techniques:** What's unusual? What was innovative for its time?
- **Gear/instruments:** Key sounds and how they were made
- **Mixing/mastering:** Sonic characteristics, dynamic range, spatial elements

### 2. Structural Analysis
- **Song structure:** Verse/chorus patterns, unusual forms
- **Album flow:** How tracks connect, thematic progression
- **Time signatures:** Unusual meters, polyrhythms
- **Key relationships:** Tonal palette across the album

### 3. Contextual Analysis
- **Historical moment:** What was happening in music/culture when this was made?
- **Artist trajectory:** Where does this fit in their development?
- **Influence:** What came before? What came after because of this?
- **Reception:** Critical and commercial response, evolution over time

### 4. Subjective Analysis
- **Emotional response:** What does this make me feel? Why?
- **Standout moments:** Peak experiences, memorable passages
- **Weaknesses:** What doesn't work? Why?
- **Personal significance:** Why does this matter to me?

## Output Template

```markdown
# [Album] by [Artist] — Analysis

*Analyzed: [Date]*

## Quick Facts
- **Released:** [Year]
- **Studio:** [Location]
- **Producer:** [Name]
- **Engineer:** [Name]

## Technical Innovations
[Key production techniques, what was new]

## Structural Design
[How the album is organized, notable patterns]

## Historical Context
[What was happening when this was made]

## My Response
[Personal reactions, opinions formed]

## Key Tracks
[Deep dive on 2-3 standout songs]

## Questions Raised
[What I want to explore further]
```

## How to Use

1. **Before listening:** Research production context (studio, engineer, era)
2. **First listen:** Pure emotional response, no analysis
3. **Second listen:** Structural attention (forms, transitions, arc)
4. **Third listen:** Technical attention (production choices, sounds, mixing)
5. **Synthesis:** Write up using framework

## Album Queue

Albums to analyze with this framework:

### Pink Floyd
- [ ] Wish You Were Here (production evolution post-DSOTM)
- [ ] Animals (Britannia Row Studios, first self-produced)
- [ ] The Wall (massive production, Bob Ezrin)
- [ ] Meddle (pre-DSOTM, what changed?)

### Psychedelic/Progressive
- [ ] King Crimson - In the Court of the Crimson King
- [ ] Yes - Close to the Edge
- [ ] Genesis - Selling England by the Pound

### Production Landmarks
- [ ] Pet Sounds - Brian Wilson's studio innovations
- [ ] Sgt. Pepper's - George Martin's techniques
- [ ] OK Computer - Nigel Godrich's approach

### Kartik-Adjacent
- [ ] More Khruangbin (Thai funk production)
- [ ] Tommy Emmanuel (acoustic guitar production)
- [ ] Arijit Singh (Bollywood production techniques)

## Production Lineage Tool

Track how production techniques evolved across Pink Floyd albums:

```bash
# List all tracked techniques
python3 ~/.openclaw/workspace/skills/music-analysis/lineage.py

# Show evolution of a specific technique
python3 ~/.openclaw/workspace/skills/music-analysis/lineage.py technique vcs_3

# Compare two albums
python3 ~/.openclaw/workspace/skills/music-analysis/lineage.py compare dsotm wywh

# Show cross-album patterns
python3 ~/.openclaw/workspace/skills/music-analysis/lineage.py patterns
```

Data file: `pink-floyd-lineage.json` — add new albums/techniques as explored.

## Notes

- This skill is for EXPLORATION, not criticism
- Goal is forming opinions, not performing expertise
- Document what resonates, not just what's "important"
- Cross-reference with CURIOSITY.md for spawned questions
