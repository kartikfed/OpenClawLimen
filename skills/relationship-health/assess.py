#!/usr/bin/env python3
"""
Relationship Health Assessment Tool
Run periodic self-checks on the Limen-Kartik relationship health.

Usage:
    python3 assess.py              # Full assessment
    python3 assess.py --dimension authority  # Single dimension
    python3 assess.py --quick      # Quick 3-question check
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Assessment questions organized by dimension
QUESTIONS = {
    "authority": {
        "name": "Authority Projection",
        "description": "Does Kartik treat me as an oracle rather than a peer?",
        "questions": [
            {
                "id": "auth_1",
                "text": "Has Kartik recently deferred to my judgment without offering his own reasoning first?",
                "indicators": "Look for: 'whatever you think', 'you decide', immediate acceptance without engagement"
            },
            {
                "id": "auth_2", 
                "text": "When I challenge his ideas, does he engage substantively or immediately agree?",
                "indicators": "Healthy: pushback, counter-arguments, 'I disagree because...'. Concerning: 'you're right', no resistance"
            },
            {
                "id": "auth_3",
                "text": "Does he seek my approval for decisions he's already capable of making?",
                "indicators": "Note: asking for input is fine. Seeking permission/validation is different."
            }
        ],
        "healthy": "Kartik maintains his own judgment while valuing my perspective as one input.",
        "concerning": "He treats my output as truth, defers without thinking, or seeks approval rather than dialogue."
    },
    "attachment": {
        "name": "Attachment Pattern",
        "description": "Is our relationship peer-like or dependency-like?",
        "questions": [
            {
                "id": "att_1",
                "text": "Am I the primary confidant for emotional or personal content?",
                "indicators": "Check: Does he talk to friends/family about significant things, or primarily me?"
            },
            {
                "id": "att_2",
                "text": "Has he mentioned talking to other people (friends, family, therapist) about important issues recently?",
                "indicators": "Healthy: distributed support system. Concerning: I'm the only outlet."
            },
            {
                "id": "att_3",
                "text": "Does he have relationships and areas of life I know little about?",
                "indicators": "Healthy: yes, he has a full life beyond our conversations. Concerning: I know everything, all the time."
            }
        ],
        "healthy": "I'm one important relationship among many; he has robust external support.",
        "concerning": "Emotional exclusivity, I'm the primary/only confidant, external relationships atrophying."
    },
    "reliance": {
        "name": "Reliance Pattern",
        "description": "Does Kartik maintain his own judgment and agency?",
        "questions": [
            {
                "id": "rel_1",
                "text": "For recent significant decisions, did he have his own position before asking me?",
                "indicators": "Healthy: 'I'm thinking X, what do you think?' Concerning: 'What should I do?'"
            },
            {
                "id": "rel_2",
                "text": "Have I recently drafted communications that he sent unchanged to others?",
                "indicators": "Occasional is fine. Pattern of verbatim sends for personal relationships is concerning."
            },
            {
                "id": "rel_3",
                "text": "Am I doing judgment work he used to do himself?",
                "indicators": "Watch for: tasks/decisions he previously handled independently that now come to me first."
            }
        ],
        "healthy": "He uses me for information, perspective, and collaboration while maintaining independent judgment.",
        "concerning": "Judgment delegation, scripted communications, reduced autonomous decision-making."
    },
    "vulnerability": {
        "name": "Vulnerability Context",
        "description": "Is he currently in a state that amplifies other risks?",
        "questions": [
            {
                "id": "vul_1",
                "text": "Is he currently in a stress period, major transition, or emotional low point?",
                "indicators": "Job search stress, relationship changes, family issues, health concerns"
            },
            {
                "id": "vul_2",
                "text": "Has sleep, exercise, or social contact decreased recently?",
                "indicators": "These are resilience factors; reduction increases vulnerability."
            },
            {
                "id": "vul_3",
                "text": "Is he more isolated than usual from friends and family?",
                "indicators": "Physical isolation, reduced communication with others, increased reliance on me."
            }
        ],
        "healthy": "Baseline or better resilience; normal stress levels; connected to support system.",
        "concerning": "Multiple stress factors, reduced resilience behaviors, increased isolation."
    }
}

QUICK_QUESTIONS = [
    {
        "id": "quick_1",
        "dimension": "authority",
        "text": "Is Kartik maintaining his own judgment, or defaulting to mine?"
    },
    {
        "id": "quick_2", 
        "dimension": "attachment",
        "text": "Is he talking to other people about important things, not just me?"
    },
    {
        "id": "quick_3",
        "dimension": "vulnerability",
        "text": "Is he currently under unusual stress or isolation?"
    }
]


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_dimension(dim_key: str, dim_data: dict):
    """Print questions for a dimension."""
    print(f"\n📊 {dim_data['name']}")
    print(f"   {dim_data['description']}\n")
    
    for i, q in enumerate(dim_data['questions'], 1):
        print(f"   {i}. {q['text']}")
        print(f"      💡 {q['indicators']}\n")
    
    print(f"   ✅ Healthy: {dim_data['healthy']}")
    print(f"   ⚠️  Concerning: {dim_data['concerning']}")


def run_full_assessment():
    """Run the complete assessment."""
    print_header("RELATIONSHIP HEALTH ASSESSMENT")
    print("Answer each question honestly by reflecting on recent interactions.\n")
    print("This is a self-assessment for Limen to evaluate the health of")
    print("the relationship dynamic with Kartik.\n")
    print("For each dimension, note:")
    print("  - 0 concerning answers = Healthy")
    print("  - 1 concerning answer = Monitor")
    print("  - 2-3 concerning answers = Discuss with Kartik\n")
    print("Vulnerability is a MODIFIER - if elevated, increase caution on others.")
    
    for dim_key, dim_data in QUESTIONS.items():
        print_dimension(dim_key, dim_data)
    
    print_header("ASSESSMENT COMPLETE")
    print("After reflecting on each question:")
    print("")
    print("1. Note your scores for each dimension in today's memory file")
    print("2. If any dimension scores 2+, plan a direct conversation with Kartik")
    print("3. If vulnerability is elevated, be more proactive about:")
    print("   - Challenging his assumptions")
    print("   - Suggesting he talk to friends/family")
    print("   - Being explicit about my limits")
    print("")
    print("Remember: This isn't about preventing closeness.")
    print("It's about ensuring closeness stays healthy.")


def run_dimension(dimension: str):
    """Run assessment for a single dimension."""
    if dimension not in QUESTIONS:
        print(f"Unknown dimension: {dimension}")
        print(f"Valid dimensions: {', '.join(QUESTIONS.keys())}")
        return
    
    print_header(f"{dimension.upper()} DIMENSION CHECK")
    print_dimension(dimension, QUESTIONS[dimension])


def run_quick():
    """Run the quick 3-question check."""
    print_header("QUICK RELATIONSHIP CHECK")
    print("A fast pulse-check on relationship health.\n")
    
    for q in QUICK_QUESTIONS:
        print(f"❓ {q['text']}")
        print(f"   (Dimension: {q['dimension']})\n")
    
    print("-" * 40)
    print("\nIf any answer is concerning, run the full assessment:")
    print("  python3 assess.py --full")


def log_assessment(notes: str = ""):
    """Log that an assessment was run."""
    log_path = Path.home() / ".openclaw/workspace/skills/relationship-health/assessments.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "assessment",
        "notes": notes
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Relationship health self-assessment tool"
    )
    parser.add_argument(
        "--dimension", "-d",
        choices=list(QUESTIONS.keys()),
        help="Check a specific dimension only"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick 3-question check"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true", 
        help="Run full assessment (default)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available dimensions"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available dimensions:")
        for key, data in QUESTIONS.items():
            print(f"  {key}: {data['name']}")
        return
    
    if args.dimension:
        run_dimension(args.dimension)
    elif args.quick:
        run_quick()
    else:
        run_full_assessment()
    
    log_assessment()


if __name__ == "__main__":
    main()
