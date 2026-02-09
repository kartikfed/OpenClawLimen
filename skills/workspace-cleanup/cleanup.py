#!/usr/bin/env python3
"""
Workspace Cleanup - Ultra-conservative garbage collector.

Only removes reinstallable dependencies and cache files.
Allowlist-only approach: if it's not explicitly safe, don't touch it.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple


class CleanupItem(NamedTuple):
    path: str
    size_bytes: int
    reason: str


WORKSPACE = Path.home() / ".openclaw" / "workspace"

# === ALLOWLIST: Only these patterns are considered for deletion ===

# Directory names that are safe to delete (reinstallable)
SAFE_DIR_NAMES = {
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

# Specific paths relative to workspace that are safe to clear
SAFE_CACHE_PATHS = [
    ".cache/knowledge-graph",
]

# === PROTECTED: Never touch these, even if they match patterns ===

PROTECTED_DIRS = {
    "memory",
    "secrets", 
    "scripts",
    "library",
    "kitchen",
    "docs",
    "chronicle",
    "writing",
    "substack",
    "prompts",
    "identity",
}

# Never delete files with these extensions
PROTECTED_EXTENSIONS = {
    ".md", ".py", ".ts", ".js", ".jsx", ".tsx", ".sh",
    ".json", ".yaml", ".yml", ".toml", ".txt", ".html", ".css",
}


def get_dir_size(path: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def format_size(bytes_size: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"


def is_protected_path(path: Path) -> bool:
    """Check if path is in a protected directory."""
    parts = path.relative_to(WORKSPACE).parts
    if parts and parts[0] in PROTECTED_DIRS:
        return True
    return False


def find_cleanable_dirs() -> list[CleanupItem]:
    """Find directories that are safe to delete."""
    items = []
    
    for dirpath in WORKSPACE.rglob("*"):
        if not dirpath.is_dir():
            continue
            
        # Check if this is a safe-to-delete directory name
        if dirpath.name not in SAFE_DIR_NAMES:
            continue
            
        # Skip if in protected path
        if is_protected_path(dirpath):
            continue
            
        # Skip if inside skills/ but it's the skill's own code
        # (we clean node_modules IN skills, not the skills themselves)
        
        size = get_dir_size(dirpath)
        if size > 0:
            items.append(CleanupItem(
                path=str(dirpath),
                size_bytes=size,
                reason=f"Reinstallable dependency ({dirpath.name})"
            ))
    
    return items


def find_cleanable_caches() -> list[CleanupItem]:
    """Find cache directories that are safe to clear."""
    items = []
    
    for cache_path in SAFE_CACHE_PATHS:
        full_path = WORKSPACE / cache_path
        if full_path.exists() and full_path.is_dir():
            size = get_dir_size(full_path)
            if size > 0:
                items.append(CleanupItem(
                    path=str(full_path),
                    size_bytes=size,
                    reason="Regenerated cache"
                ))
    
    return items


def find_stale_crons() -> list[dict]:
    """Find cron jobs that should be cleaned up."""
    stale_jobs = []
    
    try:
        # Get cron list via openclaw
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json", "--include-disabled"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return []
            
        data = json.loads(result.stdout)
        jobs = data.get("jobs", [])
        
        now = datetime.now()
        cutoff = now - timedelta(hours=24)
        cutoff_ms = int(cutoff.timestamp() * 1000)
        
        for job in jobs:
            # Disabled jobs older than 24h
            if not job.get("enabled", True):
                updated = job.get("updatedAtMs", 0)
                if updated < cutoff_ms:
                    stale_jobs.append({
                        "id": job["id"],
                        "name": job.get("name", "unnamed"),
                        "reason": "Disabled >24h"
                    })
                    
            # Completed one-shots
            if job.get("deleteAfterRun") and job.get("state", {}).get("lastStatus") == "ok":
                stale_jobs.append({
                    "id": job["id"],
                    "name": job.get("name", "unnamed"),
                    "reason": "Completed one-shot"
                })
                
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
        
    return stale_jobs


def delete_directory(path: str) -> bool:
    """Safely delete a directory."""
    try:
        shutil.rmtree(path)
        return True
    except (PermissionError, OSError) as e:
        print(f"  ⚠️  Failed to delete {path}: {e}")
        return False


def delete_cron(job_id: str) -> bool:
    """Delete a cron job."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "remove", job_id],
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def generate_confirmation_token(items: list, crons: list) -> str:
    """Generate a short token based on what will be deleted."""
    content = json.dumps({
        "paths": [i.path for i in items],
        "crons": [c["id"] for c in crons]
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:8]


def main():
    parser = argparse.ArgumentParser(description="Workspace cleanup (ultra-conservative)")
    parser.add_argument("--execute", action="store_true", help="Actually delete (default is dry-run)")
    parser.add_argument("--crons", action="store_true", help="Also clean stale cron jobs")
    parser.add_argument("--json", action="store_true", help="Output JSON for programmatic use")
    parser.add_argument("--confirm", type=str, help="Confirmation token (required with --execute)")
    args = parser.parse_args()
    
    if not args.json:
        print("🔍 Scanning workspace for cleanable items...\n")
    
    # Find cleanable items
    dir_items = find_cleanable_dirs()
    cache_items = find_cleanable_caches()
    all_items = dir_items + cache_items
    
    stale_crons = find_stale_crons() if args.crons else []
    
    # Calculate totals
    total_size = sum(item.size_bytes for item in all_items)
    
    # Generate confirmation token
    token = generate_confirmation_token(all_items, stale_crons)
    
    # JSON output mode
    if args.json:
        output = {
            "items": [
                {
                    "path": str(Path(item.path).relative_to(WORKSPACE)),
                    "full_path": item.path,
                    "size_bytes": item.size_bytes,
                    "size_human": format_size(item.size_bytes),
                    "reason": item.reason
                }
                for item in sorted(all_items, key=lambda x: x.size_bytes, reverse=True)
            ],
            "crons": stale_crons,
            "total_bytes": total_size,
            "total_human": format_size(total_size),
            "confirmation_token": token,
            "clean": len(all_items) == 0 and len(stale_crons) == 0
        }
        print(json.dumps(output, indent=2))
        return 0
    
    if not all_items and not stale_crons:
        print("✨ Workspace is clean! Nothing to remove.")
        return 0
    
    # Display findings
    print("📁 Directories to clean:")
    print("-" * 60)
    
    if all_items:
        # Sort by size descending
        all_items.sort(key=lambda x: x.size_bytes, reverse=True)
        
        for item in all_items:
            rel_path = str(Path(item.path).relative_to(WORKSPACE))
            print(f"  {format_size(item.size_bytes):>8}  {rel_path}")
            print(f"           └─ {item.reason}")
        
        print("-" * 60)
        print(f"  {'TOTAL':>8}  {format_size(total_size)}")
    else:
        print("  (none)")
    
    if args.crons and stale_crons:
        print(f"\n🕐 Stale cron jobs ({len(stale_crons)}):")
        print("-" * 60)
        for job in stale_crons:
            print(f"  • {job['name']} ({job['reason']})")
    
    print(f"\n🔑 Confirmation token: {token}")
    
    # Execute or dry-run message
    print()
    if not args.execute:
        print("🔒 DRY RUN - Nothing deleted.")
        print(f"   To delete, run with: --execute --confirm {token}")
        return 0
    
    # Verify confirmation token
    if args.confirm != token:
        print("❌ Invalid or missing confirmation token.")
        print(f"   Expected: {token}")
        print("   Run without --execute first to get the current token.")
        return 1
    
    # Actually delete
    print("🧹 Cleaning...")
    
    deleted_size = 0
    for item in all_items:
        if delete_directory(item.path):
            deleted_size += item.size_bytes
            rel_path = str(Path(item.path).relative_to(WORKSPACE))
            print(f"  ✓ Deleted {rel_path}")
    
    if args.crons:
        for job in stale_crons:
            if delete_cron(job["id"]):
                print(f"  ✓ Removed cron: {job['name']}")
    
    print()
    print(f"✅ Cleaned {format_size(deleted_size)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
