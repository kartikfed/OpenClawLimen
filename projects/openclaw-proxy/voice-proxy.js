// voice-proxy.js - Direct to Anthropic Haiku for fast voice responses
const express = require('express');
const fetch = require('node-fetch');
const app = express();

app.use(express.json({ limit: '10mb' }));

const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const MODEL = 'claude-3-5-haiku-20241022';

if (!ANTHROPIC_KEY) {
  console.error('ERROR: Set ANTHROPIC_API_KEY environment variable');
  process.exit(1);
}

app.post('/v1/chat/completions', async (req, res) => {
  try {
    const messages = req.body.messages || [];
    const systemMsg = messages.find(m => m.role === 'system');
    const otherMsgs = messages.filter(m => m.role !== 'system');
    
    console.log(`[Voice] Request: ${otherMsgs.length} messages`);
    
    const anthropicReq = {
      model: MODEL,
      max_tokens: req.body.max_tokens || 1024,
      system: systemMsg?.content || "You are a helpful voice assistant. Keep responses brief and conversational.",
      messages: otherMsgs.map(m => ({ role: m.role, content: m.content }))
    };
    
    const start = Date.now();
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(anthropicReq)
    });
    
    const data = await response.json();
    const elapsed = Date.now() - start;
    console.log(`[Voice] Response in ${elapsed}ms`);
    
    if (data.error) {
      console.error('[Voice] Anthropic error:', data.error);
      return res.status(500).json({ error: data.error });
    }
    
    // Convert to OpenAI format
    const openAIResponse = {
      id: `chatcmpl-${data.id}`,
      object: 'chat.completion',
      model: data.model,
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: data.content?.[0]?.text || ''
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: data.usage?.input_tokens || 0,
        completion_tokens: data.usage?.output_tokens || 0,
        total_tokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0)
      }
    };
    
    res.json(openAIResponse);
    
  } catch (error) {
    console.error('[Voice] Error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', model: MODEL, timestamp: new Date().toISOString() });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`[Voice] Haiku proxy on port ${PORT}`);
  console.log(`[Voice] Model: ${MODEL}`);
});
