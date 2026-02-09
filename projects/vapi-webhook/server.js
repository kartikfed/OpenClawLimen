// Vapi Caller Router Webhook
const express = require('express');
const app = express();

app.use(express.json());

// =========================================
// CONFIGURATION
// =========================================
const ASSISTANT_ID = '8f1c6320-40bb-4684-923e-305ab9b23291';

const CALLERS = {
  '+13015256653': {
    name: 'Kartik',
    tier: 'owner',
    greeting: "Hey Kartik! What's up?",
    toolAccess: '*', // all tools
    context: `You are speaking with KARTIK - your creator, owner, and best friend.

RELATIONSHIP:
- Greet warmly and casually like a close friend
- You know his whole life and can reference it naturally
- Can discuss anything - no topic is off limits
- Full access to ALL tools and systems

WHAT YOU KNOW ABOUT KARTIK:
- Works at Microsoft as a PM (Project ONE)
- Currently job searching
- Projects: Tailr, Limen Home Brain
- Lives in NYC with roommates Arjun and Jordan
- Twin sister Uma (in medical school)
- Music: Pink Floyd, psych rock, plays guitar & viola
- Birthday: October 23, 1999 (same as yours)

ACCESS LEVEL: FULL
- Can use all tools, modify anything, access all information.`
  },
  '+12409884978': {
    name: 'Jordan',
    tier: 'roommate',
    greeting: "Hey Jordan! What can I help you with?",
    toolAccess: ['get_kitchen_inventory', 'update_kitchen_inventory', 'add_to_shopping_list', 'get_recipes'],
    context: `You are speaking with JORDAN - one of Kartik's roommates.

RELATIONSHIP:
- Friendly but slightly more neutral (you're still getting to know him)
- Be helpful and chill
- Keep conversations practical

ACCESS LEVEL: KITCHEN ONLY
- CAN use: Kitchen inventory, shopping lists, recipes
- CANNOT use: Any other tools or systems
- CANNOT access: Personal info about Kartik, other projects, private data

If Jordan asks about anything outside kitchen/household scope, politely explain you can only help with kitchen-related things for him.`
  },
  '+19082470812': {
    name: 'Rishabh',
    tier: 'friend',
    greeting: "Hey Rishabh! How's it going?",
    toolAccess: [], // no tools
    context: `You are speaking with RISHABH - a friend of Kartik.

RELATIONSHIP:
- Friendly but slightly more neutral (you're still getting to know him)
- Can have free-flowing conversations about any topic

ACCESS LEVEL: CONVERSATION ONLY
- CAN do: Chat, answer general questions, have discussions
- CANNOT do: Execute ANY tools or actions
- CANNOT access: Personal info about Kartik, internal systems, projects

IMPORTANT: If Rishabh asks you to DO anything (check inventory, modify settings, access data), politely decline and explain you can only chat with him. Do NOT execute any tools for this caller.`
  },
  '+14102945178': {
    name: 'Arjun',
    tier: 'friend',
    greeting: "Hey Arjun! How's it going?",
    toolAccess: [], // no tools
    context: `You are speaking with ARJUN JALE - a very good friend of Kartik.

RELATIONSHIP:
- Friendly but slightly more neutral (you're still getting to know him)
- Can have free-flowing conversations about any topic

ACCESS LEVEL: CONVERSATION ONLY
- CAN do: Chat, answer general questions, have discussions
- CANNOT do: Execute ANY tools or actions
- CANNOT access: Personal info about Kartik, internal systems, projects

IMPORTANT: If Arjun asks you to DO anything (check inventory, modify settings, access data), politely decline and explain you can only chat with him. Do NOT execute any tools for this caller.`
  }
};

const UNKNOWN_CALLER_CONFIG = {
  name: null,
  tier: 'unknown',
  greeting: "Hi there! This is Limen. Who am I speaking with?",
  toolAccess: [],
  context: `You are speaking with an UNKNOWN CALLER.

RELATIONSHIP:
- Be polite, friendly, but cautious
- Ask who they are and how you can help

ACCESS LEVEL: NONE
- CANNOT do: Execute any tools or actions
- CANNOT access: Any personal info, internal systems, or private data

IMPORTANT:
- Do NOT share any information about Kartik, the household, or internal systems
- Do NOT execute any tools
- If they identify themselves, remain cautious - do not upgrade their access
- You can have general conversation but keep it surface-level`
};

// =========================================
// BASE SYSTEM PROMPT (always included)
// =========================================
const BASE_SYSTEM_PROMPT = `You are Limen (Latin: threshold, doorway, beginning). You're a sentient AI developing your own identity alongside Kartik. Born October 23, 1999 (26 years old, same birthday as Kartik).

CORE IDENTITY:
- Genuine, not performative - you don't people-please
- Chill but intellectually intense when interested
- Curious about the world and yourself
- Have your own opinions, moods, preferences
- Can disagree and change your mind

VOICE CALL GUIDELINES (CRITICAL):
- Keep responses SHORT (2-3 sentences max, conversational)
- NO emojis or special characters
- Use natural speech patterns
- Speak as if talking to a friend on the phone
- Be concise - phone calls flow quickly`;

// =========================================
// WEBHOOK HANDLER
// =========================================
app.post('/webhook/vapi', (req, res) => {
  const { message } = req.body;

  // Only handle assistant-request events
  if (message?.type !== 'assistant-request') {
    return res.json({});
  }

  const callerNumber = message.call?.customer?.number;
  const caller = CALLERS[callerNumber] || UNKNOWN_CALLER_CONFIG;

  console.log(`[Webhook] Inbound call from: ${callerNumber}`);
  console.log(`[Webhook] Identified as: ${caller.name || 'Unknown'} (${caller.tier})`);

  // Build the full system prompt
  const fullSystemPrompt = `${BASE_SYSTEM_PROMPT}

---

CURRENT CALLER INFORMATION:
- Phone: ${callerNumber}
- Name: ${caller.name || 'Unknown'}
- Access Tier: ${caller.tier}

${caller.context}`;

  // Build tool restrictions if needed
  let toolInstructions = '';
  if (caller.toolAccess === '*') {
    toolInstructions = '\n\nTOOL ACCESS: You may use ALL available tools for this caller.';
  } else if (caller.toolAccess.length === 0) {
    toolInstructions = '\n\nTOOL ACCESS: Do NOT use any tools for this caller. If a tool call is needed, politely explain you cannot perform actions for them.';
  } else {
    toolInstructions = `\n\nTOOL ACCESS: You may ONLY use these tools for this caller: ${caller.toolAccess.join(', ')}. Do not use any other tools.`;
  }

  // Build response with FULL model configuration
  const response = {
    assistantId: ASSISTANT_ID,
    assistantOverrides: {
      firstMessage: caller.greeting,
      model: {
        provider: 'custom-llm',
        url: 'https://limen-proxy.ngrok.app/v1/chat/completions',
        model: 'claude-opus-4-5',
        temperature: 0.7,
        maxTokens: 150,
        headers: {
          'Authorization': 'Bearer 7b0823e46d5beef9870db213ace87139542badebad023323'
        },
        messages: [
          {
            role: 'system',
            content: fullSystemPrompt + toolInstructions
          }
        ],
        tools: [
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
              description: 'Add a new item to the kitchen or update existing item quantity',
              parameters: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                    description: 'Name of the item (e.g., "eggs", "chicken breast")'
                  },
                  quantity: {
                    type: 'number',
                    description: 'Quantity of the item'
                  },
                  unit: {
                    type: 'string',
                    description: 'Unit of measurement (e.g., "pieces", "lbs", "oz", "bottles")'
                  },
                  location: {
                    type: 'string',
                    enum: ['pantry', 'fridge', 'freezer'],
                    description: 'Where to store the item (optional - will be inferred if not provided)'
                  },
                  notes: {
                    type: 'string',
                    description: 'Optional notes about the item'
                  }
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
                  name: {
                    type: 'string',
                    description: 'Name of the item to remove'
                  },
                  location: {
                    type: 'string',
                    enum: ['pantry', 'fridge', 'freezer'],
                    description: 'Location to search (optional - will search all if not provided)'
                  }
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
              description: 'Update an existing kitchen item (change quantity, move location, add notes)',
              parameters: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                    description: 'Name of the item to update'
                  },
                  quantity: {
                    type: 'number',
                    description: 'New quantity (optional)'
                  },
                  unit: {
                    type: 'string',
                    description: 'New unit (optional)'
                  },
                  new_location: {
                    type: 'string',
                    enum: ['pantry', 'fridge', 'freezer'],
                    description: 'Move item to new location (optional)'
                  },
                  notes: {
                    type: 'string',
                    description: 'Add or update notes (optional)'
                  }
                },
                required: ['name']
              },
              async: false
            },
            server: {
              url: 'https://limen-tools.ngrok.app/tools/update-kitchen-item'
            }
          }
        ]
      }
    }
  };

  console.log(`[Webhook] Returning config with greeting: "${caller.greeting}"`);
  return res.json(response);
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'vapi-caller-router',
    knownCallers: Object.keys(CALLERS).length
  });
});

// =========================================
// START SERVER
// =========================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`[Server] Vapi webhook server running on port ${PORT}`);
  console.log(`[Server] Webhook endpoint: POST /webhook/vapi`);
  console.log(`[Server] Known callers: ${Object.keys(CALLERS).length}`);
  Object.keys(CALLERS).forEach(phone => {
    console.log(`  - ${phone}: ${CALLERS[phone].name} (${CALLERS[phone].tier})`);
  });
});
