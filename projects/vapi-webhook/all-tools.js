// All available tools for voice agent
// Tools are filtered per-caller based on allowlist

const ALL_TOOLS = [
  // Kitchen tools
  {
    type: 'function',
    function: {
      name: 'get_kitchen_inventory',
      description: 'Check what food and ingredients are in the kitchen',
      parameters: {
        type: 'object',
        properties: {
          location: {
            type: 'string',
            enum: ['all', 'pantry', 'fridge', 'freezer'],
            description: 'Which location to check'
          }
        }
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/kitchen-inventory'
    }
  },
  {
    type: 'function',
    function: {
      name: 'add_kitchen_item',
      description: 'Add a new item to the kitchen or update quantity',
      parameters: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Item name' },
          quantity: { type: 'number', description: 'Quantity' },
          unit: { type: 'string', description: 'Unit of measurement' },
          location: { type: 'string', enum: ['pantry', 'fridge', 'freezer'], description: 'Where to store (optional)' },
          notes: { type: 'string', description: 'Optional notes' }
        },
        required: ['name', 'quantity', 'unit']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/add-kitchen-item'
    }
  },
  {
    type: 'function',
    function: {
      name: 'remove_kitchen_item',
      description: 'Remove an item from the kitchen inventory',
      parameters: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Item name to remove' },
          location: { type: 'string', enum: ['pantry', 'fridge', 'freezer'], description: 'Location (optional)' }
        },
        required: ['name']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/remove-kitchen-item'
    }
  },
  {
    type: 'function',
    function: {
      name: 'update_kitchen_item',
      description: 'Update an existing kitchen item',
      parameters: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Item name' },
          quantity: { type: 'number', description: 'New quantity (optional)' },
          unit: { type: 'string', description: 'New unit (optional)' },
          new_location: { type: 'string', enum: ['pantry', 'fridge', 'freezer'], description: 'Move to new location (optional)' },
          notes: { type: 'string', description: 'Notes (optional)' }
        },
        required: ['name']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/update-kitchen-item'
    }
  },
  
  // Memory tools
  {
    type: 'function',
    function: {
      name: 'memory_search',
      description: 'Search memory files (MEMORY.md and recent daily files) for information, facts, or context',
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'What to search for' }
        },
        required: ['query']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/memory-search'
    }
  },
  {
    type: 'function',
    function: {
      name: 'memory_update',
      description: 'Add new information to today\'s memory file during a conversation',
      parameters: {
        type: 'object',
        properties: {
          content: { type: 'string', description: 'Information to remember' },
          section: { type: 'string', description: 'Section title (default: Voice Call Notes)' }
        },
        required: ['content']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/memory-update'
    }
  },
  {
    type: 'function',
    function: {
      name: 'file_read',
      description: 'Read specific memory or documentation files (MEMORY.md, SOUL.md, USER.md, daily memory files, docs/)',
      parameters: {
        type: 'object',
        properties: {
          file_path: { type: 'string', description: 'Path to file' },
          max_lines: { type: 'number', description: 'Maximum lines to read (default: 100)' }
        },
        required: ['file_path']
      },
      async: false
    },
    server: {
      url: 'https://limen-tools.ngrok.app/tools/file-read'
    }
  }
];

function filterToolsForCaller(toolAccess) {
  // toolAccess can be:
  // - '*' (all tools)
  // - [] (no tools)
  // - ['tool_name', 'pattern_*', ...] (specific tools or patterns)
  
  if (toolAccess === '*') {
    return ALL_TOOLS;
  }
  
  if (!toolAccess || toolAccess.length === 0) {
    return [];
  }
  
  // Filter tools based on allowlist
  return ALL_TOOLS.filter(tool => {
    const toolName = tool.function.name;
    
    return toolAccess.some(pattern => {
      if (pattern === toolName) {
        return true; // Exact match
      }
      
      // Handle wildcards
      if (pattern.includes('*')) {
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return regex.test(toolName);
      }
      
      return false;
    });
  });
}

module.exports = {
  ALL_TOOLS,
  filterToolsForCaller
};
