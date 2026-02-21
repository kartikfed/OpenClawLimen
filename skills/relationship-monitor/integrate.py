#!/usr/bin/env python3
"""
Integration script for relationship monitor.
Updates state.json with relationship health data for Mission Control.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


STATE_PATH = Path.home() / ".openclaw/workspace/state.json"
MONITOR_PATH = Path(__file__).parent / "monitor.py"


def get_health_data() -> dict:
    """Run monitor and get JSON output."""
    try:
        result = subprocess.run(
            ["python3", str(MONITOR_PATH), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


def update_state():
    """Update state.json with relationship health data."""
    # Get current state
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}
    
    # Get health data
    health = get_health_data()
    
    if "error" not in health:
        summary = health.get("summary", {})
        state["relationshipHealth"] = {
            "status": summary.get("status", "unknown"),
            "adjustedConcern": summary.get("adjusted_concern", 0),
            "trend": summary.get("trend", "stable"),
            "scores": summary.get("scores", {}),
            "lastChecked": datetime.now().isoformat()
        }
        
        # Save state
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
        
        print(f"✅ Updated state.json with relationship health: {summary.get('status', 'unknown')}")
    else:
        print(f"❌ Error getting health data: {health['error']}")


def quick_status() -> str:
    """Get quick status string for logging."""
    try:
        result = subprocess.run(
            ["python3", str(MONITOR_PATH), "--quick", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return f"🩺 {data.get('status', 'unknown').upper()} (trend: {data.get('trend', 'stable')})"
    except:
        pass
    return "🩺 CHECK_FAILED"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        print(quick_status())
    else:
        update_state()
