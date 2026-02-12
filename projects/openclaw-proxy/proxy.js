// proxy.js - Translation proxy between Vapi and OpenClaw
const express = require('express');
const fetch = require('node-fetch');
const app = express();

app.use(express.json({ limit: '10mb' }));

// Direct to Anthropic API for fast voice responses
const ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages';
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY || '';  // Set this in environment
const VOICE_MODEL = 'claude-3-5-haiku-20241022';

// ============================================
// OpenAI → Claude (Request Translation)
// ============================================
function translateRequestToClaude(openAIRequest) {
  const systemMsg = openAIRequest.messages?.find(m => m.role === 'system');
  const otherMsgs = openAIRequest.messages?.filter(m => m.role !== 'system') || [];

  return {
    // Force Haiku for real-time voice (fast responses required)
    model: 'anthropic/claude-3-5-haiku-20241022',
    max_tokens: openAIRequest.max_tokens || 4096,
    system: systemMsg?.content,
    messages: translateMessagesToClaude(otherMsgs),
    tools: translateToolsToClaude(openAIRequest.tools),
    temperature: openAIRequest.temperature,
    stream: openAIRequest.stream
  };
}

function translateToolsToClaude(tools) {
  if (!tools?.length) return undefined;
  
  return tools.map(tool => ({
    name: tool.function.name,
    description: tool.function.description,
    input_schema: tool.function.parameters
  }));
}

function translateMessagesToClaude(messages) {
  const result = [];
  
  for (const msg of messages) {
    if (msg.role === 'tool') {
      // Tool result → Claude format
      result.push({
        role: 'user',
        content: [{
          type: 'tool_result',
          tool_use_id: msg.tool_call_id,
          content: msg.content
        }]
      });
    } else if (msg.role === 'assistant' && msg.tool_calls) {
      // Assistant with tool calls → Claude format
      result.push({
        role: 'assistant',
        content: msg.tool_calls.map(tc => ({
          type: 'tool_use',
          id: tc.id,
          name: tc.function.name,
          input: JSON.parse(tc.function.arguments)
        }))
      });
    } else {
      // Regular message
      result.push({
        role: msg.role,
        content: msg.content
      });
    }
  }
  
  return result;
}

// ============================================
// Claude → OpenAI (Response Translation)
// ============================================
function translateResponseToOpenAI(claudeResponse) {
  const content = claudeResponse.content || [];
  const toolUses = content.filter(c => c.type === 'tool_use');
  const textBlocks = content.filter(c => c.type === 'text');
  
  const message = { role: 'assistant' };
  let finishReason = 'stop';
  
  if (toolUses.length > 0) {
    message.content = null;
    message.tool_calls = toolUses.map(tool => ({
      id: tool.id,
      type: 'function',
      function: {
        name: tool.name,
        arguments: JSON.stringify(tool.input)
      }
    }));
    finishReason = 'tool_calls';
  } else {
    message.content = textBlocks.map(t => t.text).join(' ');
  }
  
  return {
    id: `chatcmpl-${claudeResponse.id || Date.now()}`,
    object: 'chat.completion',
    model: claudeResponse.model,
    choices: [{
      index: 0,
      message,
      finish_reason: finishReason
    }],
    usage: {
      prompt_tokens: claudeResponse.usage?.input_tokens || 0,
      completion_tokens: claudeResponse.usage?.output_tokens || 0,
      total_tokens: (claudeResponse.usage?.input_tokens || 0) + (claudeResponse.usage?.output_tokens || 0)
    }
  };
}

// ============================================
// Proxy Endpoint
// ============================================
app.post('/v1/chat/completions', async (req, res) => {
  try {
    console.log('[Proxy] Incoming request from Vapi');
    console.log('[Proxy] Tools:', req.body.tools?.length || 0);
    
    // Translate OpenAI format → Claude format
    const claudeRequest = translateRequestToClaude(req.body);
    console.log('[Proxy] Translated tools:', claudeRequest.tools?.length || 0);
    
    // Forward translated request to OpenClaw
    const response = await fetch(OPENCLAW_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': OPENCLAW_AUTH
      },
      body: JSON.stringify(claudeRequest)
    });
    
    const data = await response.json();
    console.log('[Proxy] OpenClaw response type:', data.choices?.[0]?.message ? 'OpenAI format' : 'Claude format');
    
    // Check if response is in Claude format (has content array)
    if (data.content && Array.isArray(data.content)) {
      console.log('[Proxy] Translating Claude format to OpenAI');
      const openAIResponse = translateResponseToOpenAI(data);
      return res.json(openAIResponse);
    }
    
    // Already OpenAI format - pass through
    console.log('[Proxy] Passing through OpenAI format');
    res.json(data);
    
  } catch (error) {
    console.error('[Proxy] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`[Proxy] Translation proxy running on port ${PORT}`);
  console.log(`[Proxy] Forwarding to: ${OPENCLAW_URL}`);
});
