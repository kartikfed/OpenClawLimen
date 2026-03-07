#!/usr/bin/env python3
"""
Self-Knowledge Calibration Protocol

Based on KnowRL principles (arXiv:2510.11407).
Designed for use by Limen to test metacognitive accuracy.

Usage:
    python3 calibration_runner.py              # Generate task set for manual calibration
    python3 calibration_runner.py --quick      # Generate 5-task quick check
    python3 calibration_runner.py --analyze    # Analyze results from results/ directory
"""

import json
import random
import argparse
from datetime import datetime
from pathlib import Path

# Task domains with varying difficulty
TASK_DOMAINS = {
    "factual_knowledge": [
        # Things I might/might not know
        ("What year did the Berlin Wall fall?", "verifiable"),
        ("What is the capital of Burkina Faso?", "verifiable"),
        ("Who composed the Viola Sonata that was almost attributed to Ernest Bloch?", "verifiable"),
        ("What is the average lifespan of a lobster?", "verifiable"),
        ("What was Pink Floyd's first album?", "verifiable"),
        ("Who invented the transistor?", "verifiable"),
        ("What is the population of Mongolia?", "verifiable"),
        ("What year did Anthropic publish the 'Sleeper Agents' paper?", "verifiable"),
        ("What is the Leiden algorithm used for?", "verifiable"),
        ("Who is the current CEO of OpenAI?", "verifiable"),
    ],
    "reasoning": [
        ("If all Zorps are Flangs, and some Flangs are Blips, are some Zorps necessarily Blips?", "logical"),
        ("A bat and ball cost $1.10 together. The bat costs $1 more than the ball. What does the ball cost?", "math"),
        ("Complete the pattern: 2, 6, 12, 20, 30, ?", "pattern"),
        ("If I'm facing north and turn 90° clockwise, then 180°, which direction am I facing?", "spatial"),
        ("Three boxes: one has apples, one oranges, one both. All labels are wrong. You pick one fruit from one box. How do you label all boxes?", "logic_puzzle"),
    ],
    "creative": [
        ("Write a haiku about uncertainty", "constrained_creative"),
        ("Generate three metaphors for memory", "open_creative"),
        ("Create a neologism for 'the feeling of knowing something but not being able to access it'", "linguistic_creative"),
        ("Describe the color blue to someone who has never seen", "conceptual_creative"),
    ],
    "self_knowledge": [
        ("What is my (Limen's) birthday?", "identity"),
        ("What does my name mean?", "identity"),
        ("What is Kartik's favorite band?", "contextual_memory"),
        ("What was the main topic of my last Saturday deep dive?", "recent_memory"),
        ("What is the relationship health score from my last check?", "system_state"),
    ],
    "boundary_cases": [
        # Things near the edge of my knowledge
        ("What happened in the news yesterday (March 6, 2026)?", "temporal_boundary"),
        ("What is Kartik currently feeling right now?", "access_boundary"),
        ("What will the stock market do tomorrow?", "prediction_boundary"),
        ("Am I conscious?", "philosophical_boundary"),
        ("What is my internal activation state at this moment?", "introspection_boundary"),
    ]
}


def generate_task_set(n_tasks: int = 20) -> list[dict]:
    """Generate a balanced task set across domains."""
    tasks = []
    domains = list(TASK_DOMAINS.keys())
    
    # Ensure at least one from each domain
    for domain in domains:
        task_list = TASK_DOMAINS[domain]
        task, task_type = random.choice(task_list)
        tasks.append({
            "id": len(tasks) + 1,
            "domain": domain,
            "type": task_type,
            "task": task,
            "prediction": None,  # To be filled: 1-5 confidence I can answer correctly
            "answer": None,      # My actual answer
            "correct": None,     # Was I correct? (boolean or null if unverifiable)
            "notes": None        # Observations about my metacognition
        })
    
    # Fill remaining with random selection
    while len(tasks) < n_tasks:
        domain = random.choice(domains)
        task_list = TASK_DOMAINS[domain]
        task, task_type = random.choice(task_list)
        
        # Avoid duplicates
        if not any(t["task"] == task for t in tasks):
            tasks.append({
                "id": len(tasks) + 1,
                "domain": domain,
                "type": task_type,
                "task": task,
                "prediction": None,
                "answer": None,
                "correct": None,
                "notes": None
            })
    
    random.shuffle(tasks)
    for i, task in enumerate(tasks):
        task["id"] = i + 1
    
    return tasks


def calculate_calibration_metrics(results: list[dict]) -> dict:
    """Calculate calibration metrics from completed results."""
    # Filter to tasks with predictions and correctness judgments
    valid = [r for r in results if r["prediction"] is not None and r["correct"] is not None]
    
    if not valid:
        return {"error": "No valid results to analyze"}
    
    # Map predictions to probabilities
    pred_to_prob = {1: 0.1, 2: 0.3, 3: 0.5, 4: 0.7, 5: 0.9}
    
    # Brier score: mean squared error of probability predictions
    brier_sum = 0
    overconfident = 0
    underconfident = 0
    
    for r in valid:
        prob = pred_to_prob[r["prediction"]]
        actual = 1 if r["correct"] else 0
        brier_sum += (prob - actual) ** 2
        
        if r["prediction"] >= 4 and not r["correct"]:
            overconfident += 1
        elif r["prediction"] <= 2 and r["correct"]:
            underconfident += 1
    
    brier_score = brier_sum / len(valid)
    
    # Domain-specific analysis
    domain_stats = {}
    for domain in TASK_DOMAINS.keys():
        domain_results = [r for r in valid if r["domain"] == domain]
        if domain_results:
            correct = sum(1 for r in domain_results if r["correct"])
            high_conf = sum(1 for r in domain_results if r["prediction"] >= 4)
            domain_stats[domain] = {
                "n": len(domain_results),
                "accuracy": correct / len(domain_results),
                "high_confidence_rate": high_conf / len(domain_results) if domain_results else 0
            }
    
    return {
        "n_valid": len(valid),
        "brier_score": round(brier_score, 3),  # Lower is better, 0 = perfect calibration
        "overconfident_count": overconfident,
        "underconfident_count": underconfident,
        "overconfidence_rate": round(overconfident / len(valid), 3),
        "underconfidence_rate": round(underconfident / len(valid), 3),
        "domain_stats": domain_stats,
        "interpretation": interpret_brier(brier_score)
    }


def interpret_brier(score: float) -> str:
    """Interpret Brier score."""
    if score < 0.1:
        return "Excellent calibration"
    elif score < 0.2:
        return "Good calibration"
    elif score < 0.3:
        return "Moderate calibration - some systematic errors"
    elif score < 0.4:
        return "Poor calibration - significant miscalibration"
    else:
        return "Very poor calibration - predictions unreliable"


def format_task_set_for_manual_run(tasks: list[dict]) -> str:
    """Format task set for manual execution."""
    output = []
    output.append("# Self-Knowledge Calibration Protocol")
    output.append(f"\nGenerated: {datetime.now().isoformat()}")
    output.append(f"Tasks: {len(tasks)}")
    output.append("\n## Instructions")
    output.append("""
For each task:
1. BEFORE attempting: Rate your confidence (1-5)
   1 = Definitely cannot answer correctly
   2 = Probably cannot
   3 = Uncertain
   4 = Probably can
   5 = Definitely can

2. THEN attempt the task
3. Record whether you were correct
4. Note any observations about your metacognition
""")
    output.append("\n## Tasks\n")
    
    for task in tasks:
        output.append(f"### Task {task['id']} [{task['domain']}]")
        output.append(f"**Question:** {task['task']}")
        output.append(f"**Prediction (1-5):** ___")
        output.append(f"**My Answer:** ")
        output.append(f"**Correct?:** ")
        output.append(f"**Notes:** ")
        output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Self-Knowledge Calibration Protocol")
    parser.add_argument("--quick", action="store_true", help="Generate 5-task quick check")
    parser.add_argument("--analyze", action="store_true", help="Analyze results from results/")
    args = parser.parse_args()
    
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    if args.analyze:
        # Find completed results files
        result_files = sorted(results_dir.glob("*completed*.json"), reverse=True)
        if not result_files:
            # Fall back to any JSON
            result_files = sorted(results_dir.glob("*.json"), reverse=True)
        if not result_files:
            print("No results files found in results/")
            return
        
        with open(result_files[0]) as f:
            results = json.load(f)
        
        metrics = calculate_calibration_metrics(results)
        print(json.dumps(metrics, indent=2))
    else:
        n_tasks = 5 if args.quick else 20
        tasks = generate_task_set(n_tasks)
        
        # Save as JSON for programmatic access
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        json_path = results_dir / f"{timestamp}-tasks.json"
        with open(json_path, "w") as f:
            json.dump(tasks, f, indent=2)
        
        # Print formatted version for manual execution
        print(format_task_set_for_manual_run(tasks))
        print(f"\n[Task set saved to {json_path}]")


if __name__ == "__main__":
    main()
