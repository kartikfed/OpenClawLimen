// post-call-handler.js - Save voice call transcripts to memory
const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(express.json({ limit: '10mb' }));

const WORKSPACE = path.join(process.env.HOME, '.openclaw', 'workspace');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

function getTodayFileName() {
  const today = new Date();
  return `${today.toISOString().split('T')[0]}.md`; // YYYY-MM-DD.md
}

function formatTranscript(callData) {
  const timestamp = new Date().toLocaleString('en-US', { 
    timeZone: 'America/New_York',
    hour12: false 
  });
  
  const caller = callData.customer?.number || 'Unknown';
  const duration = Math.round((callData.endedAt - callData.startedAt) / 1000);  // seconds
  const transcript = callData.transcript || '';
  const summary = callData.summary || 'No summary available';
  
  return `
## Voice Call - ${caller} (${timestamp})

**Duration:** ${duration} seconds
**Call ID:** ${callData.id}

**Summary:** ${summary}

**Transcript:**
\`\`\`
${transcript}
\`\`\`

**Tools used:**
${callData.messages?.filter(m => m.toolCalls).map(m => 
  m.toolCalls.map(tc => `- ${tc.function.name}`).join('\n')
).join('\n') || 'None'}

---
`;
}

// POST /webhook/post-call
app.post('/webhook/post-call', (req, res) => {
  try {
    const { message } = req.body;
    
    if (message?.type !== 'end-of-call-report') {
      return res.json({ received: true });
    }
    
    const callData = message.call;
    console.log(`[PostCall] Received end-of-call report for: ${callData.id}`);
    console.log(`[PostCall] Caller: ${callData.customer?.number}`);
    
    // Format the transcript
    const formattedTranscript = formatTranscript(callData);
    
    // Append to today's memory file
    const todayFile = path.join(MEMORY_DIR, getTodayFileName());
    
    // Create memory directory if it doesn't exist
    if (!fs.existsSync(MEMORY_DIR)) {
      fs.mkdirSync(MEMORY_DIR, { recursive: true });
    }
    
    // Append to file (or create if doesn't exist)
    fs.appendFileSync(todayFile, formattedTranscript);
    
    console.log(`[PostCall] Transcript saved to: ${todayFile}`);
    
    return res.json({ 
      received: true,
      saved: true,
      file: getTodayFileName()
    });
    
  } catch (error) {
    console.error('[PostCall] Error saving transcript:', error);
    return res.status(500).json({ 
      error: error.message,
      received: true,
      saved: false
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    service: 'vapi-post-call-handler'
  });
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`[PostCall] Post-call webhook handler running on port ${PORT}`);
  console.log(`[PostCall] Endpoint: POST /webhook/post-call`);
  console.log(`[PostCall] Memory dir: ${MEMORY_DIR}`);
});
