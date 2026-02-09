#!/usr/bin/env python3
"""
Linear CLI for Limen
Usage:
  linear.py list                    - List my open issues
  linear.py create "title"          - Create issue
  linear.py update <id> --done      - Mark issue done
  linear.py comment <id> "text"     - Add comment
"""

import sys
import json
import requests
from pathlib import Path

TOKEN_FILE = Path.home() / ".openclaw/workspace/secrets/linear-access-token.txt"
TEAM_ID = "dc1f97e3-8c84-42ab-91dd-92a48d5f0f9c"  # Thicc LLC
LIMEN_ID = "0b19adc9-9a91-4eca-943a-c469a5a6c45b"

# Workflow state IDs
STATES = {
    "backlog": "b0e29163-7a15-492c-9bab-f063b26e4368",
    "todo": "471c2a9b-6b50-4c7e-a18a-a27129418407",
    "in_progress": "9aeaac56-7c3f-402c-8cb4-ca9d73db1387",
    "done": "e29f9db9-d328-4564-ae57-c3d5b577ea40",
    "canceled": "ae5a2252-f5c5-4fc9-86e7-c0d5056caac0",
}

def get_token():
    return TOKEN_FILE.read_text().strip()

def gql(query, variables=None):
    resp = requests.post(
        "https://api.linear.app/graphql",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_token()}",
        },
        json={"query": query, "variables": variables or {}},
    )
    data = resp.json()
    if "errors" in data:
        print(f"Error: {data['errors']}", file=sys.stderr)
        sys.exit(1)
    return data["data"]

def list_issues():
    """List open issues (assigned to Limen or unassigned in team)"""
    query = """
    query {
      team(id: "%s") {
        issues(first: 50, filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
          nodes {
            id identifier title priority
            state { name }
            assignee { name }
            createdAt
          }
        }
      }
    }
    """ % TEAM_ID
    
    data = gql(query)
    issues = data["team"]["issues"]["nodes"]
    
    if not issues:
        print("No open issues!")
        return
    
    print(f"\n{'ID':<8} {'Priority':<10} {'State':<12} {'Assignee':<10} {'Title'}")
    print("-" * 80)
    
    priority_map = {0: "None", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}
    
    for issue in sorted(issues, key=lambda x: x["priority"] or 5):
        assignee = issue["assignee"]["name"][:8] if issue["assignee"] else "-"
        priority = priority_map.get(issue["priority"], "?")
        state = issue["state"]["name"][:10]
        print(f"{issue['identifier']:<8} {priority:<10} {state:<12} {assignee:<10} {issue['title'][:40]}")

def create_issue(title, description="", priority=2, assign_to_limen=False):
    """Create a new issue"""
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue { id identifier title url }
      }
    }
    """
    
    input_data = {
        "teamId": TEAM_ID,
        "title": title,
        "description": description,
        "priority": priority,
    }
    
    if assign_to_limen:
        input_data["assigneeId"] = LIMEN_ID
    
    data = gql(mutation, {"input": input_data})
    issue = data["issueCreate"]["issue"]
    print(f"✅ Created: {issue['identifier']} - {issue['title']}")
    print(f"   URL: {issue['url']}")
    return issue

def get_issue_id_from_identifier(identifier):
    """Convert identifier like THI-26 to issue UUID"""
    # Parse identifier (e.g., "THI-26" -> number 26)
    parts = identifier.split("-")
    if len(parts) != 2:
        print(f"Invalid identifier format: {identifier}")
        sys.exit(1)
    
    try:
        issue_number = int(parts[1])
    except ValueError:
        print(f"Invalid issue number in identifier: {identifier}")
        sys.exit(1)
    
    query = """
    query FindIssue($teamId: ID!, $number: Float!) {
      issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $number } }, first: 1) {
        nodes { id identifier }
      }
    }
    """
    
    data = gql(query, {"teamId": TEAM_ID, "number": issue_number})
    issues = data["issues"]["nodes"]
    
    if not issues:
        print(f"Issue {identifier} not found")
        sys.exit(1)
    
    return issues[0]["id"]

def update_issue(identifier, state=None, priority=None, title=None):
    """Update an issue"""
    issue_id = get_issue_id_from_identifier(identifier)
    
    mutation = """
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue { id identifier title state { name } }
      }
    }
    """
    
    input_data = {}
    if state:
        input_data["stateId"] = STATES.get(state, state)
    if priority is not None:
        input_data["priority"] = priority
    if title:
        input_data["title"] = title
    
    data = gql(mutation, {"id": issue_id, "input": input_data})
    issue = data["issueUpdate"]["issue"]
    print(f"✅ Updated: {issue['identifier']} - {issue['title']} [{issue['state']['name']}]")

def add_comment(identifier, body):
    """Add a comment to an issue"""
    issue_id = get_issue_id_from_identifier(identifier)
    
    mutation = """
    mutation CreateComment($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment { id body }
      }
    }
    """
    
    data = gql(mutation, {"input": {"issueId": issue_id, "body": body}})
    print(f"✅ Comment added to {identifier}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_issues()
    
    elif cmd == "create":
        if len(sys.argv) < 3:
            print("Usage: linear.py create \"title\" [--description \"...\"] [--priority N] [--mine]")
            sys.exit(1)
        
        title = sys.argv[2]
        description = ""
        priority = 2
        assign = False
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--description" and i + 1 < len(sys.argv):
                description = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--mine":
                assign = True
                i += 1
            else:
                i += 1
        
        create_issue(title, description, priority, assign)
    
    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: linear.py update <ID> [--done|--todo|--progress] [--priority N]")
            sys.exit(1)
        
        identifier = sys.argv[2]
        state = None
        priority = None
        
        for arg in sys.argv[3:]:
            if arg == "--done":
                state = "done"
            elif arg == "--todo":
                state = "todo"
            elif arg == "--progress":
                state = "in_progress"
            elif arg == "--backlog":
                state = "backlog"
            elif arg.startswith("--priority="):
                priority = int(arg.split("=")[1])
        
        update_issue(identifier, state, priority)
    
    elif cmd == "comment":
        if len(sys.argv) < 4:
            print("Usage: linear.py comment <ID> \"comment text\"")
            sys.exit(1)
        
        identifier = sys.argv[2]
        body = sys.argv[3]
        add_comment(identifier, body)
    
    elif cmd == "done":
        if len(sys.argv) < 3:
            print("Usage: linear.py done <ID>")
            sys.exit(1)
        update_issue(sys.argv[2], state="done")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
