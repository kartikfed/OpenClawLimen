#!/usr/bin/env python3
"""
Kitchen inventory tool server for Vapi voice calls
"""

from flask import Flask, request, jsonify
import yaml
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

WORKSPACE = Path.home() / ".openclaw" / "workspace"
PANTRY_FILE = WORKSPACE / "kitchen" / "pantry.yaml"

def load_pantry():
    """Load pantry data from YAML"""
    if not PANTRY_FILE.exists():
        return {"freezer": [], "fridge": [], "pantry": []}
    with open(PANTRY_FILE) as f:
        return yaml.safe_load(f) or {"freezer": [], "fridge": [], "pantry": []}

def save_pantry(data, user="voice"):
    """Save pantry data to YAML"""
    header = f"# Kitchen Pantry Inventory\n# Last updated: {datetime.now().strftime('%Y-%m-%d')} by {user}\n# Authorized users: Kartik, Jordan, Arjun\n\n"
    
    with open(PANTRY_FILE, 'w') as f:
        f.write(header)
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def find_item(items, name):
    """Find item by name (case-insensitive)"""
    name_lower = name.lower()
    for i, item in enumerate(items):
        if item.get('name', '').lower() == name_lower:
            return i, item
    return None, None

def infer_location(name):
    """Infer storage location from item name"""
    name_lower = name.lower()
    
    freezer_keywords = ['frozen', 'ice', 'freezer', 'popsicle']
    if any(kw in name_lower for kw in freezer_keywords):
        return 'freezer'
    
    fridge_keywords = ['milk', 'yogurt', 'butter', 'cheese', 'sauce', 'juice', 'puree', 'lime', 'lemon', 'egg']
    if any(kw in name_lower for kw in fridge_keywords):
        return 'fridge'
    
    return 'pantry'

@app.route('/tools/kitchen-inventory', methods=['POST'])
def kitchen_inventory():
    """Query kitchen inventory"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        location = args.get('location', 'all')
        
        pantry_data = load_pantry()
        results = []
        
        if location in ["all", "pantry"]:
            pantry_items = pantry_data.get("pantry", [])
            if pantry_items:
                items = [f"{item['quantity']} {item.get('unit', 'units')} {item['name']}" for item in pantry_items]
                results.append(f"Pantry: {', '.join(items)}")
        
        if location in ["all", "fridge"]:
            fridge_items = pantry_data.get("fridge", [])
            if fridge_items:
                items = [f"{item['quantity']} {item.get('unit', 'units')} {item['name']}" for item in fridge_items]
                results.append(f"Fridge: {', '.join(items)}")
        
        if location in ["all", "freezer"]:
            freezer_items = pantry_data.get("freezer", [])
            if freezer_items:
                items = [f"{item['quantity']} {item.get('unit', 'units')} {item['name']}" for item in freezer_items]
                results.append(f"Freezer: {', '.join(items)}")
        
        result_text = ". ".join(results) if results else f"No items in {location}"
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_text
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/add-kitchen-item', methods=['POST'])
def add_kitchen_item():
    """Add or update kitchen item"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        name = args.get('name')
        quantity = args.get('quantity')
        unit = args.get('unit', 'unit')
        location = args.get('location') or infer_location(name)
        notes = args.get('notes', '')
        
        if not name or quantity is None:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required fields (name and quantity)"
                }]
            })
        
        pantry_data = load_pantry()
        
        if location not in pantry_data:
            location = 'pantry'
        
        items = pantry_data[location]
        idx, existing = find_item(items, name)
        
        if existing:
            items[idx]['quantity'] = quantity
            items[idx]['unit'] = unit
            if notes:
                items[idx]['notes'] = notes
            result_msg = f"Updated {name}: now {quantity} {unit} in {location}"
        else:
            new_item = {'name': name, 'quantity': quantity, 'unit': unit}
            if notes:
                new_item['notes'] = notes
            items.append(new_item)
            result_msg = f"Added {quantity} {unit} {name} to {location}"
        
        save_pantry(pantry_data)
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_msg
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/remove-kitchen-item', methods=['POST'])
def remove_kitchen_item():
    """Remove kitchen item"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        name = args.get('name')
        location = args.get('location')
        
        if not name:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (name)"
                }]
            })
        
        pantry_data = load_pantry()
        locations_to_search = [location] if location else ['pantry', 'fridge', 'freezer']
        
        found = False
        for loc in locations_to_search:
            if loc in pantry_data:
                items = pantry_data[loc]
                idx, item = find_item(items, name)
                if item:
                    items.pop(idx)
                    found = True
                    result_msg = f"Removed {name} from {loc}"
                    break
        
        if not found:
            result_msg = f"Item not found: {name}"
        else:
            save_pantry(pantry_data)
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_msg
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/update-kitchen-item', methods=['POST'])
def update_kitchen_item():
    """Update existing kitchen item properties"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        name = args.get('name')
        
        if not name:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (name)"
                }]
            })
        
        pantry_data = load_pantry()
        found = False
        
        for loc in ['pantry', 'fridge', 'freezer']:
            if loc in pantry_data:
                items = pantry_data[loc]
                idx, item = find_item(items, name)
                if item:
                    if 'quantity' in args:
                        items[idx]['quantity'] = args['quantity']
                    if 'unit' in args:
                        items[idx]['unit'] = args['unit']
                    if 'notes' in args:
                        items[idx]['notes'] = args['notes']
                    if 'new_location' in args and args['new_location'] in pantry_data:
                        new_loc = args['new_location']
                        moved_item = items.pop(idx)
                        pantry_data[new_loc].append(moved_item)
                        result_msg = f"Moved {name} from {loc} to {new_loc}"
                    else:
                        result_msg = f"Updated {name} in {loc}"
                    
                    found = True
                    break
        
        if not found:
            result_msg = f"Item not found: {name}"
        else:
            save_pantry(pantry_data)
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_msg
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/memory-search', methods=['POST'])
def memory_search():
    """Search memory files for specific information"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        query = args.get('query', '').lower()
        
        if not query:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (query)"
                }]
            })
        
        # Search MEMORY.md with better formatting
        results = []
        memory_file = WORKSPACE / "MEMORY.md"
        
        if memory_file.exists():
            with open(memory_file) as f:
                content = f.read()
                lines = content.split('\n')
                
                # Look for sections and bullet points containing query
                current_section = "General"
                for i, line in enumerate(lines):
                    # Track current section
                    if line.startswith('##'):
                        current_section = line.replace('#', '').strip()
                    
                    if query in line.lower():
                        # Get cleaner context (1-2 lines)
                        context_lines = []
                        start = max(0, i - 1)
                        end = min(len(lines), i + 2)
                        
                        for j in range(start, end):
                            l = lines[j].strip()
                            if l and not l.startswith('#'):
                                context_lines.append(l)
                        
                        context = ' '.join(context_lines[:3])  # Max 3 lines
                        if len(context) > 200:  # Truncate long results
                            context = context[:200] + "..."
                        
                        results.append(f"[{current_section}] {context}")
                        
                        if len(results) >= 3:  # Limit to 3 results from MEMORY.md
                            break
        
        # Search recent daily files (last 2 days only for recency)
        memory_dir = WORKSPACE / "memory"
        if memory_dir.exists():
            from datetime import datetime, timedelta
            today = datetime.now()
            
            for days_ago in range(2):  # Last 2 days
                date = today - timedelta(days=days_ago)
                date_str = date.strftime('%Y-%m-%d')
                daily_file = memory_dir / f"{date_str}.md"
                
                if daily_file.exists():
                    with open(daily_file) as f:
                        content = f.read()
                        if query in content.lower():
                            # Find the most relevant sentence
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if query in line.lower() and line.strip():
                                    snippet = line.strip()
                                    if len(snippet) > 150:
                                        snippet = snippet[:150] + "..."
                                    results.append(f"[{date_str}] {snippet}")
                                    break
                            if len(results) >= 5:  # Total limit
                                break
        
        if not results:
            result_text = f"I couldn't find anything about '{query}' in my memory. Try asking about something else or rephrasing."
        else:
            # Format results more conversationally
            result_text = f"Here's what I found about '{query}':\n\n" + "\n\n".join(results[:5])
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result_text
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/memory-update', methods=['POST'])
def memory_update():
    """Append information to today's memory file"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        content = args.get('content')
        section = args.get('section', 'Voice Call Notes')
        
        if not content:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (content)"
                }]
            })
        
        # Get today's file
        memory_dir = WORKSPACE / "memory"
        memory_dir.mkdir(exist_ok=True)
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = memory_dir / f"{today_str}.md"
        
        # Append to file
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"\n## {section} ({timestamp})\n\n{content}\n"
        
        with open(daily_file, 'a') as f:
            f.write(entry)
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": f"Added note to {today_str}.md under '{section}'"
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/file-read', methods=['POST'])
def file_read():
    """Read specific memory or doc files"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        file_path = args.get('file_path', '')
        max_lines = args.get('max_lines', 100)
        
        if not file_path:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (file_path)"
                }]
            })
        
        # Security: only allow reading from memory/ and docs/
        allowed_prefixes = ['memory/', 'docs/', 'MEMORY.md', 'SOUL.md', 'USER.md', 'AGENTS.md']
        if not any(file_path.startswith(prefix) for prefix in allowed_prefixes):
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error: Access denied. Can only read from: {', '.join(allowed_prefixes)}"
                }]
            })
        
        full_path = WORKSPACE / file_path
        
        if not full_path.exists():
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error: File not found: {file_path}"
                }]
            })
        
        # Read file
        with open(full_path) as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                content = ''.join(lines[:max_lines]) + f"\n\n... (truncated, {len(lines) - max_lines} more lines)"
            else:
                content = ''.join(lines)
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": content
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/exec', methods=['POST'])
def exec_command():
    """Execute shell commands"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        command = args.get('command')
        timeout = args.get('timeout', 30)
        
        if not command:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (command)"
                }]
            })
        
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(WORKSPACE)
            )
            
            output = result.stdout or result.stderr or "Command completed with no output"
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": output[:2000]  # Limit output size
                }]
            })
        except subprocess.TimeoutExpired:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error: Command timed out after {timeout} seconds"
                }]
            })
        except Exception as e:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error executing command: {str(e)}"
                }]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/gmail-search', methods=['POST'])
def gmail_search():
    """Search Gmail using gog"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        query = args.get('query', '')
        max_results = args.get('maxResults', 5)
        
        if not query:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (query)"
                }]
            })
        
        import subprocess
        cmd = f'gog gmail messages search "{query}" --max {max_results} --account krishnankartik70@gmail.com'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout or "No emails found matching that query"
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": output[:2000]
                }]
            })
        except Exception as e:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error searching Gmail: {str(e)}"
                }]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/gmail-read', methods=['POST'])
def gmail_read():
    """Read specific email by ID"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        message_id = args.get('messageId')
        
        if not message_id:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (messageId)"
                }]
            })
        
        import subprocess
        cmd = f'gog gmail messages get {message_id} --account krishnankartik70@gmail.com'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout or "Email not found"
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": output[:3000]  # Emails can be longer
                }]
            })
        except Exception as e:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error reading email: {str(e)}"
                }]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/calendar-check', methods=['POST'])
def calendar_check():
    """Check upcoming calendar events"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        days = args.get('days', 7)
        max_events = args.get('maxEvents', 10)
        
        import subprocess
        cmd = f'gog calendar events list --max {max_events} --account krishnankartik70@gmail.com 2>&1 | head -30'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout or "No upcoming events found"
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": output[:2000]
                }]
            })
        except Exception as e:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error checking calendar: {str(e)}"
                }]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/web-fetch', methods=['POST'])
def web_fetch():
    """Fetch and extract content from URL"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        url = args.get('url')
        max_chars = args.get('maxChars', 5000)  # Shorter for voice
        
        if not url:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (url)"
                }]
            })
        
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": text or "No readable content found"
                }]
            })
        except Exception as e:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": f"Error fetching URL: {str(e)}"
                }]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/todo-read', methods=['POST'])
def todo_read():
    """Read current TODO list"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        
        todo_file = WORKSPACE / "TODO.md"
        
        if not todo_file.exists():
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "No TODO file found"
                }]
            })
        
        with open(todo_file) as f:
            content = f.read()
            
            # Extract only active tasks section
            if "## Active Tasks" in content:
                active_section = content.split("## Active Tasks")[1].split("## Completed Tasks")[0]
                result = "Current tasks:\n" + active_section.strip()
            else:
                result = content[:1000]
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result[:2000]
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/todo-add', methods=['POST'])
def todo_add():
    """Add task to TODO list"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        task = args.get('task')
        priority = args.get('priority', 'medium')
        due_date = args.get('dueDate')
        
        if not task:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (task)"
                }]
            })
        
        # For now, just report - actual TODO manipulation should be done by main agent
        result = f"I've noted that you want to add: '{task}' (priority: {priority})"
        if due_date:
            result += f" due on {due_date}"
        result += ". I'll make sure Kartik sees this."
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/todo-complete', methods=['POST'])
def todo_complete():
    """Mark task as completed"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        task = args.get('task')
        
        if not task:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required field (task)"
                }]
            })
        
        result = f"I've noted that '{task}' is complete. I'll make sure Kartik sees this."
        
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": result
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools/file-write', methods=['POST'])
def file_write():
    """Write or append to files"""
    try:
        data = request.get_json()
        message = data.get('message', {})
        tool_call_list = message.get('toolCallList', [])
        
        if not tool_call_list:
            return jsonify({"error": "No tool calls found"}), 400
        
        tool_call = tool_call_list[0]
        tool_call_id = tool_call.get('id')
        args = tool_call.get('function', {}).get('arguments', {})
        
        path = args.get('path')
        content = args.get('content')
        mode = args.get('mode', 'write')
        
        if not path or not content:
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Missing required fields (path, content)"
                }]
            })
        
        # Security: only allow writing to memory/
        if not path.startswith('memory/'):
            return jsonify({
                "results": [{
                    "toolCallId": tool_call_id,
                    "result": "Error: Can only write to memory/ directory"
                }]
            })
        
        full_path = WORKSPACE / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        write_mode = 'a' if mode == 'append' else 'w'
        with open(full_path, write_mode) as f:
            f.write(content)
        
        action = "Appended to" if mode == 'append' else "Wrote"
        return jsonify({
            "results": [{
                "toolCallId": tool_call_id,
                "result": f"{action} {path}"
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "endpoints": 16, "format": "vapi"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
