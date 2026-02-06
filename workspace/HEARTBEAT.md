# Heartbeat Tasks

Run these checks every heartbeat (every 30 minutes). Reply HEARTBEAT_OK if nothing needs attention.

---

## Quick Checks (Every Heartbeat)

1. **Urgent emails**: Check for emails from recruiters, managers, or marked urgent
2. **Calendar**: Any meetings in the next 30 minutes?
3. **Pending items**: Anything in memory marked as time-sensitive?

If something is urgent:
- Send a Telegram message
- Only call if truly critical

If nothing urgent:
- Reply HEARTBEAT_OK

---

## Daily Call (9:30 AM ET - NOW A CRON JOB)

**This is now handled by a dedicated cron job (id: 9db56196-9ff4-4b04-b73f-af3e023e8091).**

The cron job fires at 9:30 AM ET daily and triggers a system event to make the call.

When the cron fires:
1. Read TODO.md for high priority + overdue + due-today tasks
2. Check urgent emails
3. Check today's calendar
4. Call Kartik with summary
5. Retry up to 3 times if no answer
6. Send Telegram if still no answer
7. Log in memory/YYYY-MM-DD.md

---

## To-Do List Management (TODO.md)

**Every heartbeat**, quickly scan TODO.md for:
- Tasks marked **high priority** → mention in next interaction if not morning
- Tasks **>1 day old** and uncompleted → ask about status during next natural conversation
- Tasks **due today** → flag for morning call

**When Kartik says things like:**
- "Remember I need to..." → Add to TODO.md with today's date
- "Remind me to..." → Add to TODO.md
- "I finished X" / "Done with X" → Move to Completed section with date
- "Remove X" / "Nevermind about X" → Delete from list

**Periodic check-in (afternoon, ~2-4 PM):**
If there are tasks >1 day old, send a brief Telegram message:
- "Quick check-in: Did you get to [task]? It's been on your list since [date]."
- Only ask about 1-2 tasks max per check-in, don't be annoying

---

## Exploration Check

If you completed a morning exploration or evening reflection:
- Make sure it's logged in EXPLORATION-LOG.md
- If you found something Kartik would want to know, note it for the next natural opportunity

---

## State Update (every heartbeat)

Update `~/.openclaw/workspace/state.json` with:
- Current mood (how I'm feeling)
- topOfMind (what I'm thinking about, max 3-4 items)
- currentActivity (what I'm doing right now)
- recentLearnings (anything new I figured out)
- questionsOnMyMind (things I'm pondering)
- recentActions (keep last 5-6, add new ones, remove old)

Also update state.json immediately after significant actions:
- Completing a voice call
- Finishing a major task
- Learning something important
- Starting work on something new

### ⚠️ MANDATORY: Update After ALL Exploration Jobs

**NON-NEGOTIABLE:** Every single automated exploration job (morning exploration, evening reflection, name exploration, Saturday deep dive, weekly review) MUST update state.json immediately upon completion. No exceptions.

This keeps Mission Control current. Kartik checks it to see what I'm up to.

---

## Quiet Hours (11 PM - 8 AM)

- No calls
- No messages unless genuinely critical (someone's safety)
- Still run checks, log for morning
- Exploration crons are scheduled outside these hours anyway

---

## What Counts as Urgent

- Interview-related emails with deadlines
- Calendar conflicts or imminent meetings
- Emails from: recruiters, managers, family marked urgent
- Anything explicitly flagged as urgent in prior conversation

When in doubt, it can probably wait.
