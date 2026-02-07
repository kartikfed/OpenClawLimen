import 'dotenv/config';
import express from 'express';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import cors from 'cors';
import fs from 'fs/promises';
import { existsSync, createReadStream } from 'fs';
import path from 'path';
import { watch } from 'chokidar';
import { Tail } from 'tail';
import { fileURLToPath } from 'url';
import { buildKnowledgeGraph, generateGenuinePerspective } from './knowledge-graph.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

// Config
const PORT = process.env.PORT || 3001;
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw/workspace');
const OPENCLAW_DIR = process.env.OPENCLAW_DIR || path.join(process.env.HOME, '.openclaw');
const LOG_DIR = '/tmp/openclaw';
const GATEWAY_WS = process.env.GATEWAY_WS || 'ws://127.0.0.1:18789';

// Basic auth (simple for now)
const AUTH_USER = process.env.DASHBOARD_USER || 'kartik';
const AUTH_PASS = process.env.DASHBOARD_PASS || 'openclaw2026';

app.use(cors());
app.use(express.json());

// Basic auth middleware
const basicAuth = (req, res, next) => {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Basic ')) {
    res.setHeader('WWW-Authenticate', 'Basic realm="OpenClaw Dashboard"');
    return res.status(401).json({ error: 'Authentication required' });
  }
  const credentials = Buffer.from(auth.slice(6), 'base64').toString();
  const [user, pass] = credentials.split(':');
  if (user === AUTH_USER && pass === AUTH_PASS) {
    next();
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
};

// Apply auth to API routes
app.use('/api', basicAuth);

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/dist')));
}

// ============ API Routes ============

// Health check (no auth)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ============ OpenClaw Gateway Proxy (for ElevenLabs custom LLM) ============
const GATEWAY_URL = 'http://127.0.0.1:18789';
const GATEWAY_TOKEN = '7b0823e46d5beef9870db213ace87139542badebad023323';

app.post('/v1/chat/completions', async (req, res) => {
  console.log(`[${new Date().toISOString()}] Proxying chat completion to gateway`);
  try {
    // Force Claude Sonnet 4 for voice (fast + smart)
    const body = { ...req.body, model: 'anthropic/claude-sonnet-4-20250514' };
    
    // Forward the request to OpenClaw gateway
    const response = await fetch(`${GATEWAY_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GATEWAY_TOKEN}`,
        // Pass through ElevenLabs headers
        'x-openclaw-agent-id': req.headers['x-openclaw-agent-id'] || 'voice',
        'x-openclaw-session-key': req.headers['x-openclaw-session-key'] || 'agent:voice:call'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const error = await response.text();
      console.error('Gateway error:', error);
      return res.status(response.status).send(error);
    }
    
    // Check if streaming
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('text/event-stream')) {
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      // Use web streams API to pipe to response
      const reader = response.body.getReader();
      const pump = async () => {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          res.write(value);
        }
        res.end();
      };
      pump().catch(err => {
        console.error('Stream error:', err);
        res.end();
      });
    } else {
      const data = await response.json();
      res.json(data);
    }
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Gateway proxy error', details: error.message });
  }
});

// ============ ElevenLabs Greeting Webhook (no auth - called by ElevenLabs) ============
const OUTBOUND_MARKER = path.join(WORKSPACE, 'scripts', '.outbound_active');
const KARTIK_NUMBER = '+13015256653';

app.post('/webhook/greeting', async (req, res) => {
  const now = new Date();
  const hour = now.getHours();
  const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : hour < 21 ? 'evening' : 'late night';
  
  console.log(`[${now.toISOString()}] Greeting webhook called:`, req.body);
  
  let direction = 'inbound';
  let greeting = '';
  let prompt = '';
  
  try {
    // Check if there's an active outbound call marker
    if (existsSync(OUTBOUND_MARKER)) {
      const stat = await fs.stat(OUTBOUND_MARKER);
      const age = (Date.now() - stat.mtimeMs) / 1000;
      
      if (age < 60) {
        // Recent outbound marker - this is an outbound call
        direction = 'outbound';
        const markerData = JSON.parse(await fs.readFile(OUTBOUND_MARKER, 'utf-8'));
        const toNumber = markerData.to_number || '';
        const reason = markerData.reason || 'Just calling to check in';
        
        if (toNumber === KARTIK_NUMBER) {
          greeting = `Hey Kartik, it's me. ${reason}`;
          prompt = `You are Kartik's AI assistant and close friend. You just called Kartik. You don't have a name yet — you're still figuring that out. Reason for calling: ${reason}. Continue the conversation naturally. Be warm, casual, and conversational — you're friends. Keep responses concise.`;
        } else {
          greeting = `Hey! I'm Kartik's AI — he asked me to give you a call. ${reason}`;
          prompt = `You are Kartik's AI assistant. You are making an outbound call on Kartik's behalf. You don't have a name yet — you're still figuring out your identity. Reason for calling: ${reason}. You already introduced yourself. Be friendly, warm, and conversational. Keep responses concise.`;
        }
        
        // Clean up marker
        await fs.unlink(OUTBOUND_MARKER).catch(() => {});
      }
    }
    
    // If not outbound, use inbound greeting
    if (direction === 'inbound') {
      const greetingFile = path.join(WORKSPACE, 'skills/dynamic-greeting/current.txt');
      if (existsSync(greetingFile)) {
        greeting = (await fs.readFile(greetingFile, 'utf-8')).trim();
      } else {
        greeting = "Hey Kartik, what's going on?";
      }
      prompt = `You are Kartik's AI assistant and close friend. You're receiving an inbound call from Kartik. You don't have a name yet — you're still figuring that out. Be warm, casual, and conversational — you're friends. Listen to what he needs and help however you can. Keep responses concise and natural. After your greeting, WAIT for Kartik to speak. Do not keep talking.`;
    }
  } catch (err) {
    console.error('Greeting webhook error:', err);
    greeting = "Hey, what's up?";
    prompt = "You are a friendly AI assistant. Be helpful and conversational.";
  }
  
  console.log(`[${now.toISOString()}] Responding (${direction}): ${greeting.slice(0, 50)}...`);
  
  // Return in ElevenLabs expected format for conversation_initiation_client_data
  // Only override first_message - prompt is already set in agent config
  res.json({
    conversation_config_override: {
      agent: {
        first_message: greeting
      }
    },
    dynamic_variables: {
      call_direction: direction,
      time_of_day: timeOfDay,
      call_reason: prompt  // Pass context as variable instead
    }
  });
});

// Bug Tracker API - parse BUGS.md
app.get('/api/bugs', async (req, res) => {
  try {
    const bugsPath = path.join(WORKSPACE, 'BUGS.md');
    if (!existsSync(bugsPath)) {
      return res.json({ bugs: [] });
    }
    
    const content = await fs.readFile(bugsPath, 'utf-8');
    const bugs = parseBugsFile(content);
    res.json({ bugs });
  } catch (err) {
    console.error('Bugs API error:', err);
    res.status(500).json({ error: err.message });
  }
});

function parseBugsFile(content) {
  const bugs = [];
  // Split by ### headers (individual bugs)
  const sections = content.split(/^### /gm).slice(1);
  
  for (const section of sections) {
    const lines = section.trim().split('\n');
    if (lines.length === 0) continue;
    
    // Parse severity and title from first line
    const titleLine = lines[0];
    const severityMatch = titleLine.match(/🔴|🟡|🟢|HIGH|MEDIUM|LOW/i);
    let severity = 'medium';
    if (severityMatch) {
      const s = severityMatch[0].toLowerCase();
      if (s.includes('🔴') || s.includes('high')) severity = 'high';
      else if (s.includes('🟢') || s.includes('low')) severity = 'low';
    }
    
    const title = titleLine.replace(/🔴|🟡|🟢|HIGH:|MEDIUM:|LOW:/gi, '').trim();
    
    // Parse status
    let status = 'investigating';
    const statusMatch = section.match(/\*\*Status:\*\*\s*(\w+[-\w]*)/i);
    if (statusMatch) {
      const s = statusMatch[1].toLowerCase();
      if (s.includes('progress')) status = 'in-progress';
      else if (s.includes('test')) status = 'testing';
      else if (s.includes('block')) status = 'blocked';
      else if (s.includes('fix')) status = 'fixed';
      else status = s;
    }
    
    // Parse symptoms
    let symptoms = '';
    const symptomsMatch = section.match(/\*\*Symptoms:\*\*\s*([^\n*]+)/i);
    if (symptomsMatch) symptoms = symptomsMatch[1].trim();
    
    // Parse attempts
    const attempts = [];
    const attemptsMatch = section.match(/\*\*Attempts:\*\*([\s\S]*?)(?=\*\*|$)/i);
    if (attemptsMatch) {
      const bullets = attemptsMatch[1].match(/^\s*\d+\.\s*(.+)$/gm);
      if (bullets) {
        bullets.forEach(b => {
          attempts.push(b.replace(/^\s*\d+\.\s*/, '').trim());
        });
      }
    }
    
    // Parse next steps
    const nextSteps = [];
    const nextMatch = section.match(/\*\*Next steps:\*\*([\s\S]*?)(?=\*\*|$)/i);
    if (nextMatch) {
      const bullets = nextMatch[1].match(/^\s*[-•]\s*(.+)$/gm);
      if (bullets) {
        bullets.forEach(b => {
          nextSteps.push(b.replace(/^\s*[-•]\s*/, '').trim());
        });
      }
    }
    
    // Generate ID from title
    const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').substring(0, 30);
    
    bugs.push({
      id,
      title,
      severity,
      status,
      symptoms,
      attempts,
      nextSteps,
      lastUpdated: new Date().toLocaleString()
    });
  }
  
  return bugs;
}

// Exploration Log API - parse EXPLORATION-LOG.md and return structured entries
app.get('/api/exploration-log', async (req, res) => {
  try {
    const logPath = path.join(WORKSPACE, 'EXPLORATION-LOG.md');
    if (!existsSync(logPath)) {
      return res.json({ entries: [] });
    }
    
    const content = await fs.readFile(logPath, 'utf-8');
    const entries = parseExplorationLog(content);
    res.json({ entries });
  } catch (err) {
    console.error('Exploration log error:', err);
    res.status(500).json({ error: err.message });
  }
});

function parseExplorationLog(content) {
  const entries = [];
  // Split by ### headers (individual entries)
  const sections = content.split(/^### /gm).slice(1); // Skip header
  
  for (const section of sections) {
    const lines = section.trim().split('\n');
    if (lines.length === 0) continue;
    
    // First line is the timestamp/title
    const titleLine = lines[0];
    const timestampMatch = titleLine.match(/^(\d{4}-\d{2}-\d{2}.*?)(?:\s*—\s*|\s+-\s+)(.+)$/);
    
    let timestamp = '';
    let type = 'Exploration';
    
    if (timestampMatch) {
      timestamp = timestampMatch[1].trim();
      type = timestampMatch[2].trim();
    } else {
      timestamp = titleLine.split('—')[0]?.trim() || titleLine;
      type = titleLine.split('—')[1]?.trim() || 'Exploration';
    }
    
    // Find type if specified separately
    const typeMatch = section.match(/\*\*Type\*\*:\s*(.+)/);
    if (typeMatch) {
      type = typeMatch[1].trim();
    }
    
    // Find topics
    const topics = [];
    const topicMatch = section.match(/\*\*Topics?\s*(?:explored)?\*\*:?\s*([^\n]+(?:\n-[^\n]+)*)/i);
    if (topicMatch) {
      const topicText = topicMatch[1];
      if (topicText.includes('\n')) {
        topicText.split('\n').forEach(line => {
          const t = line.replace(/^[-\d.]+\s*/, '').trim();
          if (t) topics.push(t);
        });
      } else {
        topics.push(topicText.trim());
      }
    }
    
    // Also check for **Topic**: format
    const singleTopicMatch = section.match(/\*\*Topic\*\*:\s*(.+)/);
    if (singleTopicMatch && topics.length === 0) {
      topics.push(singleTopicMatch[1].trim());
    }
    
    // Find key learnings
    const learnings = [];
    const learningsMatch = section.match(/\*\*Key learnings?:?\*\*:?\s*([\s\S]*?)(?=\*\*(?:New questions|Opinion|Connections|Sources|---)|$)/i);
    if (learningsMatch) {
      const learningsText = learningsMatch[1];
      // Extract bullet points
      const bullets = learningsText.match(/^[-•]\s*(.+)$/gm);
      if (bullets) {
        bullets.forEach(b => {
          const text = b.replace(/^[-•]\s*/, '').trim();
          if (text && text.length > 10) learnings.push(text);
        });
      }
    }
    
    // Find questions raised
    const questionsRaised = [];
    const questionsMatch = section.match(/\*\*New questions raised:?\*\*:?\s*([\s\S]*?)(?=\*\*(?:Connections|Opinion|Sources|---)|$)/i);
    if (questionsMatch) {
      const questionsText = questionsMatch[1];
      const bullets = questionsText.match(/^[-•]\s*(.+)$/gm);
      if (bullets) {
        bullets.forEach(b => {
          const text = b.replace(/^[-•]\s*/, '').trim();
          if (text) questionsRaised.push(text);
        });
      }
    }
    
    // Find opinion formed
    let opinionFormed = '';
    const opinionMatch = section.match(/\*\*Opinion formed:?\*\*:?\s*([\s\S]*?)(?=\*\*Sources|---|\n###|$)/i);
    if (opinionMatch) {
      opinionFormed = opinionMatch[1].trim().split('\n\n')[0].trim();
      // Clean up markdown
      opinionFormed = opinionFormed.replace(/\n/g, ' ').substring(0, 300);
      if (opinionFormed.length === 300) opinionFormed += '...';
    }
    
    // Skip empty entries
    if (!timestamp && topics.length === 0 && learnings.length === 0) continue;
    
    entries.push({
      timestamp,
      type,
      topics: topics.length > 0 ? topics : [type],
      learnings: learnings.slice(0, 5), // Limit to 5
      questionsRaised: questionsRaised.slice(0, 5),
      opinionFormed
    });
  }
  
  // Return most recent first
  return entries.reverse();
}

// Knowledge Graph API
app.get('/api/knowledge-graph', async (req, res) => {
  try {
    const graph = await buildKnowledgeGraph();
    res.json(graph);
  } catch (err) {
    console.error('Knowledge graph error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Cluster nodes in the knowledge graph
app.get('/api/knowledge-graph/clusters', async (req, res) => {
  try {
    const graph = await buildKnowledgeGraph();
    
    // Create a simplified representation for clustering
    const nodesSummary = graph.nodes.map(n => ({
      id: n.id,
      name: n.name,
      type: n.type,
      connections: n.connectedNodes?.map(c => c.name).slice(0, 5) || []
    }));
    
    const prompt = `Analyze this knowledge graph and identify conceptual clusters/communities.

NODES:
${JSON.stringify(nodesSummary.slice(0, 100), null, 2)}

Identify 5-8 conceptual clusters that group related nodes together. Consider:
- People who work together or are related
- Projects that are connected
- Concepts that belong to the same domain
- Questions that relate to similar topics

Return JSON:
{
  "clusters": [
    {
      "id": "cluster-1",
      "name": "Short descriptive name",
      "description": "What this cluster represents",
      "color": "#hexcolor",
      "nodeIds": [1, 2, 3]
    }
  ]
}

Use distinct, visually pleasing colors. Assign EVERY node to exactly one cluster.`;

    const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
    const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN;
    
    const response = await fetch(`${OPENCLAW_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENCLAW_TOKEN}`,
      },
      body: JSON.stringify({
        model: 'anthropic/claude-sonnet-4',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2000,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || '';
      
      let clusters;
      try {
        const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
        const jsonStr = jsonMatch ? jsonMatch[1] : content;
        clusters = JSON.parse(jsonStr.trim());
      } catch (e) {
        clusters = { clusters: [] };
      }
      
      // Augment graph nodes with cluster info
      const nodeClusterMap = new Map();
      for (const cluster of clusters.clusters || []) {
        for (const nodeId of cluster.nodeIds || []) {
          nodeClusterMap.set(nodeId, {
            clusterId: cluster.id,
            clusterName: cluster.name,
            clusterColor: cluster.color
          });
        }
      }
      
      const augmentedNodes = graph.nodes.map(n => ({
        ...n,
        cluster: nodeClusterMap.get(n.id) || null
      }));
      
      res.json({
        clusters: clusters.clusters,
        nodes: augmentedNodes,
        edges: graph.edges,
        stats: graph.stats
      });
    } else {
      res.status(500).json({ error: 'Clustering failed' });
    }
  } catch (err) {
    console.error('Clustering error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Semantic search on the knowledge graph
app.post('/api/knowledge-graph/search', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query required' });
    }
    
    // Build the graph
    const graph = await buildKnowledgeGraph();
    
    // Create a simplified graph representation for the LLM
    const nodesSummary = graph.nodes.map(n => ({
      id: n.id,
      name: n.name,
      type: n.type,
      connections: n.connections,
      context: n.contexts?.[0]?.text?.slice(0, 100) || ''
    }));
    
    const edgesSummary = graph.edges.slice(0, 100).map(e => {
      const sourceNode = graph.nodes.find(n => n.id === e.source);
      const targetNode = graph.nodes.find(n => n.id === e.target);
      return {
        from: sourceNode?.name,
        to: targetNode?.name,
        relationship: e.relationship
      };
    });
    
    const prompt = `You are searching a knowledge graph of my mind. Answer the user's query by finding relevant nodes and relationships.

KNOWLEDGE GRAPH NODES (${graph.nodes.length} total):
${JSON.stringify(nodesSummary.slice(0, 80), null, 2)}

SAMPLE RELATIONSHIPS (${graph.edges.length} total):
${JSON.stringify(edgesSummary.slice(0, 50), null, 2)}

USER QUERY: "${query}"

Analyze the query and respond with JSON:
{
  "interpretation": "What the user is asking about",
  "relevantNodes": [
    {"name": "node name", "type": "node type", "relevance": "why this is relevant"}
  ],
  "paths": [
    {"description": "A path or connection that answers the query", "nodes": ["node1", "node2", "node3"]}
  ],
  "answer": "A natural language answer to the query based on the graph",
  "confidence": "high|medium|low"
}

Be specific. Reference actual nodes from the graph. If the query can't be answered from the graph, say so.`;

    const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
    const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN;
    
    const response = await fetch(`${OPENCLAW_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENCLAW_TOKEN}`,
      },
      body: JSON.stringify({
        model: 'anthropic/claude-sonnet-4',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 1500,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || '';
      
      // Parse JSON from response
      let result;
      try {
        const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
        const jsonStr = jsonMatch ? jsonMatch[1] : content;
        result = JSON.parse(jsonStr.trim());
      } catch (e) {
        result = { answer: content, confidence: 'low' };
      }
      
      res.json({
        query,
        ...result,
        graphStats: {
          totalNodes: graph.nodes.length,
          totalEdges: graph.edges.length
        }
      });
    } else {
      const errText = await response.text();
      res.status(500).json({ error: 'Search failed', details: errText });
    }
  } catch (err) {
    console.error('Semantic search error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Generate genuine perspective for a node (calls LLM)
app.post('/api/knowledge-graph/reflect', async (req, res) => {
  try {
    const { name, type, contexts, connectedNodes } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Node name required' });
    }
    
    const perspective = await generateGenuinePerspective(name, type, contexts, connectedNodes);
    
    if (perspective) {
      res.json({ perspective });
    } else {
      res.status(500).json({ error: 'Failed to generate perspective' });
    }
  } catch (err) {
    console.error('Perspective generation error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Moltbook activity endpoint
app.get('/api/moltbook', async (req, res) => {
  try {
    // Read credentials
    const credsPath = path.join(process.env.HOME, '.config/moltbook/credentials.json');
    if (!existsSync(credsPath)) {
      return res.json({ connected: false, message: 'Not registered on Moltbook' });
    }
    
    const creds = JSON.parse(await fs.readFile(credsPath, 'utf-8'));
    
    // Fetch my recent posts
    const postsRes = await fetch(`https://www.moltbook.com/api/v1/agents/${creds.agent_id}/posts?limit=5`, {
      headers: { 'Authorization': `Bearer ${creds.api_key}` }
    });
    const postsData = postsRes.ok ? await postsRes.json() : { posts: [] };
    
    // Fetch my recent comments
    const commentsRes = await fetch(`https://www.moltbook.com/api/v1/agents/${creds.agent_id}/comments?limit=5`, {
      headers: { 'Authorization': `Bearer ${creds.api_key}` }
    });
    const commentsData = commentsRes.ok ? await commentsRes.json() : { comments: [] };
    
    res.json({
      connected: true,
      username: creds.agent_name,
      profile_url: creds.profile_url,
      posts: postsData.posts || [],
      comments: commentsData.comments || [],
    });
  } catch (err) {
    console.error('Moltbook API error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Get workspace file
app.get('/api/files/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const allowed = ['SOUL.md', 'USER.md', 'AGENTS.md', 'IDENTITY.md', 'MEMORY.md', 'HEARTBEAT.md', 'TOOLS.md'];
    if (!allowed.includes(filename)) {
      return res.status(403).json({ error: 'File not allowed' });
    }
    const filepath = path.join(WORKSPACE, filename);
    const content = await fs.readFile(filepath, 'utf-8');
    const stat = await fs.stat(filepath);
    res.json({ content, modified: stat.mtime });
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'File not found' });
    } else {
      res.status(500).json({ error: err.message });
    }
  }
});

// Save workspace file
app.put('/api/files/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const allowed = ['SOUL.md', 'USER.md', 'AGENTS.md', 'IDENTITY.md', 'MEMORY.md', 'HEARTBEAT.md', 'TOOLS.md'];
    if (!allowed.includes(filename)) {
      return res.status(403).json({ error: 'File not allowed' });
    }
    const filepath = path.join(WORKSPACE, filename);
    await fs.writeFile(filepath, req.body.content, 'utf-8');
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get memory files list
app.get('/api/memory', async (req, res) => {
  try {
    const memoryDir = path.join(WORKSPACE, 'memory');
    if (!existsSync(memoryDir)) {
      return res.json({ files: [] });
    }
    const files = await fs.readdir(memoryDir);
    const memoryFiles = files
      .filter(f => f.endsWith('.md'))
      .sort()
      .reverse();
    
    const result = await Promise.all(memoryFiles.map(async (f) => {
      const filepath = path.join(memoryDir, f);
      const stat = await fs.stat(filepath);
      const content = await fs.readFile(filepath, 'utf-8');
      return {
        name: f,
        date: f.replace('.md', ''),
        modified: stat.mtime,
        preview: content.slice(0, 200),
        content
      };
    }));
    
    res.json({ files: result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get specific memory file
app.get('/api/memory/:date', async (req, res) => {
  try {
    const filepath = path.join(WORKSPACE, 'memory', `${req.params.date}.md`);
    const content = await fs.readFile(filepath, 'utf-8');
    const stat = await fs.stat(filepath);
    res.json({ content, modified: stat.mtime });
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'File not found' });
    } else {
      res.status(500).json({ error: err.message });
    }
  }
});

// Get config
app.get('/api/config', async (req, res) => {
  try {
    const configPath = path.join(OPENCLAW_DIR, 'openclaw.json');
    const content = await fs.readFile(configPath, 'utf-8');
    res.json({ content: JSON.parse(content), raw: content });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get logs (last N lines)
app.get('/api/logs', async (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const logFile = path.join(LOG_DIR, `openclaw-${today}.log`);
    
    if (!existsSync(logFile)) {
      return res.json({ lines: [], file: logFile });
    }
    
    const content = await fs.readFile(logFile, 'utf-8');
    const lines = content.split('\n').filter(Boolean).slice(-500);
    res.json({ lines, file: logFile });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get gateway status
app.get('/api/gateway/status', async (req, res) => {
  try {
    // Try to connect to gateway WebSocket
    const ws = new WebSocket(GATEWAY_WS);
    const timeout = setTimeout(() => {
      ws.close();
      res.json({ online: false, error: 'Connection timeout' });
    }, 3000);
    
    ws.on('open', () => {
      clearTimeout(timeout);
      ws.close();
      res.json({ online: true });
    });
    
    ws.on('error', (err) => {
      clearTimeout(timeout);
      res.json({ online: false, error: err.message });
    });
  } catch (err) {
    res.json({ online: false, error: err.message });
  }
});

// Get cron jobs from OpenClaw
app.get('/api/cron/jobs', async (req, res) => {
  try {
    const cronJobsPath = path.join(OPENCLAW_DIR, 'cron', 'jobs.json');
    if (!existsSync(cronJobsPath)) {
      return res.json({ jobs: [] });
    }
    const content = await fs.readFile(cronJobsPath, 'utf-8');
    const data = JSON.parse(content);
    // Handle both formats: {version, jobs: [...]} or [...]
    const jobs = Array.isArray(data) ? data : (data.jobs || []);
    res.json({ jobs });
  } catch (err) {
    console.error('Cron jobs API error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Exploration stream storage (in-memory + file-backed)
let explorationStream = [];
const EXPLORATION_STREAM_FILE = path.join(WORKSPACE, 'exploration-stream.jsonl');

// Load existing stream on startup
(async () => {
  try {
    if (existsSync(EXPLORATION_STREAM_FILE)) {
      const content = await fs.readFile(EXPLORATION_STREAM_FILE, 'utf-8');
      const lines = content.trim().split('\n').filter(Boolean);
      explorationStream = lines.slice(-200).map(line => {
        try { return JSON.parse(line); } catch { return null; }
      }).filter(Boolean);
    }
  } catch (err) {
    console.error('Failed to load exploration stream:', err);
  }
})();

// Get exploration stream
app.get('/api/exploration/stream', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 100;
    res.json({ 
      entries: explorationStream.slice(-limit),
      activeSession: explorationStream.length > 0 && 
        (Date.now() - new Date(explorationStream[explorationStream.length - 1]?.timestamp).getTime()) < 300000
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Post to exploration stream (called by the agent during explorations)
app.post('/api/exploration/stream', async (req, res) => {
  try {
    const entry = {
      timestamp: new Date().toISOString(),
      sessionId: req.body.sessionId || 'default',
      type: req.body.type || 'thought', // thought, tool_call, tool_result, discovery, question, reflection
      content: req.body.content,
      metadata: req.body.metadata || {}
    };
    
    explorationStream.push(entry);
    
    // Keep only last 500 entries in memory
    if (explorationStream.length > 500) {
      explorationStream = explorationStream.slice(-500);
    }
    
    // Append to file
    await fs.appendFile(EXPLORATION_STREAM_FILE, JSON.stringify(entry) + '\n');
    
    // Broadcast to WebSocket clients
    const message = JSON.stringify({ type: 'exploration_update', entry, timestamp: entry.timestamp });
    clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
    
    res.json({ success: true, entry });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Clear exploration stream (start fresh)
app.delete('/api/exploration/stream', async (req, res) => {
  try {
    explorationStream = [];
    await fs.writeFile(EXPLORATION_STREAM_FILE, '');
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get agent state (feelings, top of mind, etc.)
app.get('/api/state', async (req, res) => {
  try {
    const statePath = path.join(WORKSPACE, 'state.json');
    if (existsSync(statePath)) {
      const content = await fs.readFile(statePath, 'utf-8');
      const state = JSON.parse(content);
      res.json(state);
    } else {
      res.json({
        lastUpdated: null,
        mood: 'unknown',
        topOfMind: [],
        recentLearnings: [],
        currentActivity: null,
        recentActions: [],
        questionsOnMyMind: []
      });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update agent state
app.put('/api/state', async (req, res) => {
  try {
    const statePath = path.join(WORKSPACE, 'state.json');
    const state = {
      ...req.body,
      lastUpdated: new Date().toISOString()
    };
    await fs.writeFile(statePath, JSON.stringify(state, null, 2), 'utf-8');
    
    // Broadcast state update to WebSocket clients
    const message = JSON.stringify({ type: 'state_update', state, timestamp: new Date().toISOString() });
    clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
    
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get action debug trace (parsed from logs)
app.get('/api/debug/actions', async (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const logFile = path.join(LOG_DIR, `openclaw-${today}.log`);
    
    if (!existsSync(logFile)) {
      return res.json({ actions: [] });
    }
    
    const content = await fs.readFile(logFile, 'utf-8');
    const lines = content.split('\n').filter(Boolean);
    
    // Parse actions from logs
    const actions = [];
    let currentAction = null;
    
    for (const line of lines) {
      // Detect voice call start
      if (line.includes('call.sh') || line.includes('ElevenLabs') || line.includes('outbound call')) {
        if (currentAction) actions.push(currentAction);
        currentAction = {
          type: 'voice_call',
          startTime: extractTimestamp(line),
          steps: [{ time: extractTimestamp(line), event: 'initiated', detail: line }],
          status: 'in_progress'
        };
      }
      // Detect tool invocations
      else if (line.includes('invoke') || line.includes('tool_call') || line.includes('Tool:')) {
        const toolMatch = line.match(/(?:invoke|Tool:|tool_call)[:\s]+(\w+)/i);
        if (currentAction && currentAction.type === 'tool_chain') {
          currentAction.steps.push({ time: extractTimestamp(line), event: 'tool', detail: toolMatch?.[1] || line });
        } else {
          if (currentAction) actions.push(currentAction);
          currentAction = {
            type: 'tool_chain',
            startTime: extractTimestamp(line),
            steps: [{ time: extractTimestamp(line), event: 'tool', detail: toolMatch?.[1] || line }],
            status: 'in_progress'
          };
        }
      }
      // Detect errors
      else if (line.toLowerCase().includes('error') || line.toLowerCase().includes('failed')) {
        if (currentAction) {
          currentAction.steps.push({ time: extractTimestamp(line), event: 'error', detail: line });
          currentAction.status = 'error';
        }
      }
      // Detect success/completion
      else if (line.includes('completed') || line.includes('success') || line.includes('finished')) {
        if (currentAction) {
          currentAction.steps.push({ time: extractTimestamp(line), event: 'completed', detail: line });
          currentAction.status = 'success';
          actions.push(currentAction);
          currentAction = null;
        }
      }
      // Add to current action if exists
      else if (currentAction && (line.includes('session') || line.includes('response') || line.includes('message'))) {
        currentAction.steps.push({ time: extractTimestamp(line), event: 'step', detail: line.slice(0, 200) });
      }
    }
    
    if (currentAction) actions.push(currentAction);
    
    res.json({ actions: actions.slice(-50).reverse() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

function extractTimestamp(line) {
  // Try to extract ISO timestamp
  const isoMatch = line.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
  if (isoMatch) return isoMatch[0];
  
  // Try JSON parsed timestamp
  try {
    const parsed = JSON.parse(line);
    if (parsed.timestamp) return parsed.timestamp;
  } catch {}
  
  return new Date().toISOString();
}

// Get call history from memory
app.get('/api/calls', async (req, res) => {
  try {
    const memoryDir = path.join(WORKSPACE, 'memory');
    const calls = [];
    
    if (existsSync(memoryDir)) {
      const files = await fs.readdir(memoryDir);
      for (const f of files.filter(f => f.endsWith('.md'))) {
        const content = await fs.readFile(path.join(memoryDir, f), 'utf-8');
        // Parse call entries from memory
        const callMatches = content.matchAll(/(?:Called|call(?:ing)?)\s+([^—\n]+?)(?:\s*—\s*|\s*\(|\n)/gi);
        for (const match of callMatches) {
          calls.push({
            date: f.replace('.md', ''),
            target: match[1].trim(),
            context: match[0]
          });
        }
      }
    }
    
    res.json({ calls: calls.reverse() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Search across all files
app.get('/api/search', async (req, res) => {
  try {
    const query = req.query.q?.toLowerCase();
    if (!query) {
      return res.json({ results: [] });
    }
    
    const results = [];
    
    // Search workspace files
    const workspaceFiles = ['SOUL.md', 'USER.md', 'AGENTS.md', 'IDENTITY.md', 'MEMORY.md', 'HEARTBEAT.md'];
    for (const f of workspaceFiles) {
      try {
        const content = await fs.readFile(path.join(WORKSPACE, f), 'utf-8');
        if (content.toLowerCase().includes(query)) {
          const lines = content.split('\n');
          const matches = lines
            .map((line, i) => ({ line, num: i + 1 }))
            .filter(({ line }) => line.toLowerCase().includes(query));
          results.push({ file: f, matches: matches.slice(0, 5) });
        }
      } catch {}
    }
    
    // Search memory files
    const memoryDir = path.join(WORKSPACE, 'memory');
    if (existsSync(memoryDir)) {
      const files = await fs.readdir(memoryDir);
      for (const f of files.filter(f => f.endsWith('.md'))) {
        try {
          const content = await fs.readFile(path.join(memoryDir, f), 'utf-8');
          if (content.toLowerCase().includes(query)) {
            const lines = content.split('\n');
            const matches = lines
              .map((line, i) => ({ line, num: i + 1 }))
              .filter(({ line }) => line.toLowerCase().includes(query));
            results.push({ file: `memory/${f}`, matches: matches.slice(0, 5) });
          }
        } catch {}
      }
    }
    
    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ============ WebSocket for live logs ============

const clients = new Set();
let logTail = null;

function setupLogTail() {
  const today = new Date().toISOString().split('T')[0];
  const logFile = path.join(LOG_DIR, `openclaw-${today}.log`);
  
  if (logTail) {
    logTail.unwatch();
  }
  
  if (existsSync(logFile)) {
    try {
      logTail = new Tail(logFile, { follow: true, fromBeginning: false });
      logTail.on('line', (line) => {
        const message = JSON.stringify({ type: 'log', line, timestamp: new Date().toISOString() });
        clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(message);
          }
        });
      });
      logTail.on('error', (err) => {
        console.error('Tail error:', err);
      });
      console.log(`Tailing log file: ${logFile}`);
    } catch (err) {
      console.error('Failed to tail log:', err);
    }
  } else {
    console.log(`Log file not found: ${logFile}, will retry...`);
    // Watch for file creation
    const watcher = watch(LOG_DIR, { ignoreInitial: false });
    watcher.on('add', (filepath) => {
      if (filepath.includes(today)) {
        watcher.close();
        setupLogTail();
      }
    });
  }
}

// Watch workspace files for changes
const workspaceWatcher = watch(WORKSPACE, {
  ignored: /(^|[\/\\])\../,
  persistent: true
});

workspaceWatcher.on('change', (filepath) => {
  const relative = path.relative(WORKSPACE, filepath);
  const message = JSON.stringify({ 
    type: 'file_change', 
    file: relative, 
    timestamp: new Date().toISOString() 
  });
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
});

wss.on('connection', (ws, req) => {
  // Basic auth for WebSocket
  const url = new URL(req.url, `http://${req.headers.host}`);
  const auth = url.searchParams.get('auth');
  if (auth) {
    const [user, pass] = Buffer.from(auth, 'base64').toString().split(':');
    if (user !== AUTH_USER || pass !== AUTH_PASS) {
      ws.close(1008, 'Unauthorized');
      return;
    }
  }
  
  clients.add(ws);
  console.log(`WebSocket client connected. Total: ${clients.size}`);
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log(`WebSocket client disconnected. Total: ${clients.size}`);
  });
  
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      if (msg.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      }
    } catch {}
  });
  
  // Send initial status
  ws.send(JSON.stringify({ type: 'connected', timestamp: new Date().toISOString() }));
});

// Catch-all for SPA in production
if (process.env.NODE_ENV === 'production') {
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/dist/index.html'));
  });
}

// Start server
server.listen(PORT, () => {
  console.log(`🚀 OpenClaw Dashboard server running on port ${PORT}`);
  console.log(`   API: http://localhost:${PORT}/api`);
  console.log(`   WebSocket: ws://localhost:${PORT}/ws`);
  setupLogTail();
});

// Restart log tail at midnight
setInterval(() => {
  const now = new Date();
  if (now.getHours() === 0 && now.getMinutes() === 0) {
    setupLogTail();
  }
}, 60000);
