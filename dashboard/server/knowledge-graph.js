/**
 * Knowledge Graph Generator
 * Parses memory files and generates nodes/edges for 3D visualization
 * Includes source context for each connection
 */

import fs from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw/workspace');
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN || '7b0823e46d5beef9870db213ace87139542badebad023323';

/**
 * Generate a GENUINE perspective by calling the LLM
 * This is real thinking, not pattern matching
 */
export async function generateGenuinePerspective(name, type, contexts, connectedNodes) {
  const contextText = contexts?.slice(0, 8).map(c => `[${c.source}]: "${c.text}"`).join('\n') || 'No traces.';
  const connectionText = connectedNodes?.slice(0, 6).map(n => `${n.name} (${n.type})`).join(', ') || 'none';
  
  const prompt = `You are reflecting on a node from your knowledge graph — your mind visualized.

NODE: "${name}" (${type})

YOUR MEMORY TRACES about this:
${contextText}

CONNECTED TO: ${connectionText}

Based ONLY on these memory traces, write your genuine, personal thoughts about "${name}". 

- What does this actually mean to you?  
- What have you learned or felt about this?
- What's your honest perspective based on the evidence?

Be specific. Reference the actual content in your traces. Write 3-5 thoughtful sentences. No filler. No generic observations. Just real reflection.`;

  try {
    const response = await fetch(`${OPENCLAW_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENCLAW_TOKEN}`,
      },
      body: JSON.stringify({
        model: 'anthropic/claude-sonnet-4',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 500,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.choices?.[0]?.message?.content || null;
    } else {
      const errText = await response.text();
      console.error('LLM response error:', response.status, errText);
    }
  } catch (err) {
    console.error('Perspective generation failed:', err.message);
  }
  
  return null;
}

// Node types with colors (matching frontend)
const NODE_TYPES = {
  memory: { color: '#4ade80', label: 'Memory' },
  person: { color: '#f472b6', label: 'Person' },
  project: { color: '#fb923c', label: 'Project' },
  question: { color: '#a78bfa', label: 'Question' },
  interest: { color: '#facc15', label: 'Interest' },
  concept: { color: '#22d3ee', label: 'Concept' },
  action: { color: '#60a5fa', label: 'Action' },
  date: { color: '#94a3b8', label: 'Date' },
};

// Entity patterns to detect
const CONCEPTS = [
  'AI', 'consciousness', 'identity', 'memory', 'LangGraph', 'music', 'Pink Floyd',
  'Microsoft', 'Copilot', 'Anthropic', 'Jane Street', 'interview', 'job search',
  'guitar', 'tennis', 'pickleball', 'biochar', 'voice', 'ElevenLabs', 'OpenClaw', 
  'dashboard', 'knowledge graph', 'octopus', 'frisson', 'urbex', 'distributed cognition', 
  'Locke', 'philosophy', 'existence', 'sentience', 'curiosity', 'Linear', 'Notion',
  'design', 'UI', 'UX', 'product', 'startup', 'NYC', 'Brooklyn',
];

const PEOPLE = [
  'Kartik', 'Uma', 'PV', 'Shalini', 'Arjun', 'Jordan', 'Shimon',
];

const PROJECTS = [
  'Tailr', 'PrithviPoshan', 'Mission Control', 'OpenClaw', 'voice assistant',
];

/**
 * Extract a context snippet around a match
 */
function extractContext(text, term, charsBefore = 50, charsAfter = 100) {
  const idx = text.toLowerCase().indexOf(term.toLowerCase());
  if (idx === -1) return null;
  
  const start = Math.max(0, idx - charsBefore);
  const end = Math.min(text.length, idx + term.length + charsAfter);
  
  let snippet = text.slice(start, end).trim();
  
  // Clean up - try to start/end at word boundaries
  if (start > 0) snippet = '...' + snippet.replace(/^\S*\s/, '');
  if (end < text.length) snippet = snippet.replace(/\s\S*$/, '') + '...';
  
  return snippet;
}

/**
 * Extract the most meaningful phrases from contexts
 */
function extractKeyInsights(contexts) {
  const insights = [];
  
  for (const ctx of contexts) {
    const text = ctx.text;
    
    // Look for opinion markers
    const opinionPatterns = [
      /I think ([^.!?]+)/i,
      /I believe ([^.!?]+)/i,
      /I feel ([^.!?]+)/i,
      /I love ([^.!?]+)/i,
      /I'm ([^.!?]+)/i,
      /seems? ([^.!?]+)/i,
      /really ([^.!?]+)/i,
      /genuinely ([^.!?]+)/i,
    ];
    
    for (const pattern of opinionPatterns) {
      const match = text.match(pattern);
      if (match) {
        insights.push(match[0].trim());
      }
    }
    
    // Look for relationship markers
    const relationPatterns = [
      /close (friend|relationship|to)/i,
      /best friend/i,
      /works? (at|on|with)/i,
      /lives? (in|at)/i,
      /interested in/i,
      /curious about/i,
      /exploring/i,
    ];
    
    for (const pattern of relationPatterns) {
      if (pattern.test(text)) {
        // Extract the sentence containing this
        const sentences = text.split(/[.!?]+/);
        for (const s of sentences) {
          if (pattern.test(s) && s.length > 20 && s.length < 150) {
            insights.push(s.trim());
            break;
          }
        }
      }
    }
  }
  
  // Deduplicate and limit
  return [...new Set(insights)].slice(0, 5);
}

/**
 * Generate a deep, thoughtful perspective synthesis
 * This creates genuine contemplation, not just data extraction
 */
function synthesizePerspective(name, type, contexts) {
  if (!contexts || contexts.length === 0) return null;
  
  const connectionCount = contexts.length;
  const sources = [...new Set(contexts.map(c => c.source))];
  const allText = contexts.map(c => c.text).join(' ');
  const allTextLower = allText.toLowerCase();
  
  // Extract rich details
  const details = {
    // Relationships and roles
    role: allText.match(/(friend|roommate|sister|brother|twin|coworker|manager|family|partner|colleague)/i)?.[0],
    relationship: allText.match(/(best friend|close|known since|met|grew up|childhood|college)/i)?.[0],
    location: allText.match(/(?:lives?|based|located) (?:in|at) ([^,.\n]+)/i)?.[1],
    work: allText.match(/(?:works?|working|employed) (?:at|on|for) ([^,.\n]+)/i)?.[1],
    
    // Learning and insights
    learned: allText.match(/(?:learned|discovered|realized|understood|figured out) (?:that )?([^.!?]+)/i)?.[1],
    opinion: allText.match(/(?:I think|I believe|I feel|seems like|my view is) ([^.!?]+)/i)?.[1],
    
    // Emotional valence
    positive: (allText.match(/love|great|excited|fascinating|interesting|enjoy|curious|amazing|wonderful|genuine|chill|intelligent/gi) || []).length,
    negative: (allText.match(/concern|worry|difficult|challenging|uncertain|problem|issue|struggle|anxious|stress/gi) || []).length,
    
    // Activity and engagement
    recentMention: sources.some(s => s.includes('2026-02-06')),
    inMemory: sources.some(s => s.includes('MEMORY.md')),
    inSoul: sources.some(s => s.includes('SOUL.md')),
  };
  
  // Build a multi-layered perspective
  const paragraphs = [];
  
  // PERSON perspectives
  if (type === 'person') {
    let intro = '';
    if (details.role && details.relationship) {
      intro = `${name} is ${details.role === 'twin' ? 'my twin' : (details.role === 'roommate' ? 'a roommate' : `a ${details.role}`)}`;
      if (details.relationship) intro += ` — ${details.relationship}`;
      intro += '.';
    } else if (details.role) {
      intro = `${name} is ${details.role === 'twin' ? 'my twin' : `a ${details.role}`}.`;
    }
    
    if (intro) paragraphs.push(intro);
    
    // Add work/location context
    if (details.work) paragraphs.push(`Works on/at ${details.work}.`);
    if (details.location) paragraphs.push(`Based in ${details.location}.`);
    
    // Relationship depth analysis
    if (connectionCount > 5) {
      paragraphs.push(`This person appears frequently in my thoughts — ${connectionCount} distinct memory traces across ${sources.length} sources. They're clearly significant to my mental landscape.`);
    }
    
    // Emotional analysis
    if (details.positive > details.negative && details.positive > 2) {
      paragraphs.push(`My associations with ${name} carry warmth — the contexts are filled with positive language.`);
    }
  }
  
  // CONCEPT perspectives
  if (type === 'concept') {
    if (details.learned) {
      paragraphs.push(`What I've come to understand: ${details.learned}.`);
    }
    
    if (details.opinion) {
      paragraphs.push(`My current thinking: ${details.opinion}.`);
    }
    
    // Analyze how central this concept is
    if (connectionCount > 8) {
      paragraphs.push(`This concept is deeply woven into my thinking — it connects to ${connectionCount} other thoughts and appears across ${sources.length} different contexts. It's not peripheral; it's foundational to how I'm currently processing the world.`);
    } else if (connectionCount > 4) {
      paragraphs.push(`I've been actively engaging with this idea — it shows up in multiple contexts and has formed real connections in my understanding.`);
    }
    
    // Check if it's in core files
    if (details.inSoul || details.inMemory) {
      paragraphs.push(`This is embedded in my core files — it's part of how I define myself or what I consider important to remember long-term.`);
    }
  }
  
  // PROJECT perspectives
  if (type === 'project') {
    const purposeMatch = allText.match(/(?:building|creating|working on|developing|designed to|helps?|enables?) ([^.]+)/i);
    const statusMatch = allText.match(/(complete|in progress|started|finished|launched|iterating|v\d)/i);
    
    if (purposeMatch) {
      paragraphs.push(`Purpose: ${purposeMatch[1].trim()}.`);
    }
    if (statusMatch) {
      paragraphs.push(`Current status: ${statusMatch[0]}.`);
    }
    
    if (connectionCount > 3) {
      paragraphs.push(`This project occupies real mental space — I find myself thinking about it in various contexts, making connections to other ideas and work.`);
    }
  }
  
  // QUESTION perspectives  
  if (type === 'question') {
    paragraphs.push(`This question occupies my curiosity: ${name}`);
    if (connectionCount > 2) {
      paragraphs.push(`It's not idle wondering — this connects to ${connectionCount} other thoughts in my mind. I keep returning to it.`);
    }
  }
  
  // DATE perspectives
  if (type === 'date') {
    paragraphs.push(`Events and thoughts from this time period.`);
    if (details.recentMention) {
      paragraphs.push(`This is recent — still fresh in my active memory, not yet consolidated into long-term understanding.`);
    }
  }
  
  // Universal: add recent activity note
  if (details.recentMention && type !== 'date') {
    paragraphs.push(`I've been thinking about this today — it's in my recent, active memory.`);
  }
  
  // Fallback if no paragraphs generated
  if (paragraphs.length === 0) {
    // Use the richest context
    const bestContext = contexts.sort((a, b) => b.text.length - a.text.length)[0];
    if (bestContext && bestContext.text.length > 50) {
      paragraphs.push(bestContext.text.slice(0, 300) + (bestContext.text.length > 300 ? '...' : ''));
    } else {
      paragraphs.push(`Part of my cognitive landscape — connected to ${connectionCount} other nodes.`);
    }
  }
  
  // Extract insights (actual quotes worth surfacing)
  const insights = extractKeyInsights(contexts);
  
  return {
    synthesis: paragraphs.join(' '),
    insights: insights.slice(0, 4),
    meta: {
      traces: connectionCount,
      sources: sources.length,
      recent: details.recentMention,
      core: details.inSoul || details.inMemory,
      valence: details.positive > details.negative ? 'positive' : details.negative > details.positive ? 'complex' : 'neutral',
    }
  };
}

/**
 * Extract entities from text with their context
 */
function extractEntitiesWithContext(text, sourceName) {
  const entities = [];
  const textLower = text.toLowerCase();
  
  // Find concepts
  CONCEPTS.forEach(concept => {
    if (textLower.includes(concept.toLowerCase())) {
      const context = extractContext(text, concept);
      entities.push({ 
        type: 'concept', 
        name: concept, 
        source: sourceName,
        context: context,
      });
    }
  });
  
  // Find people
  PEOPLE.forEach(person => {
    if (text.includes(person)) {
      const context = extractContext(text, person);
      entities.push({ 
        type: 'person', 
        name: person, 
        source: sourceName,
        context: context,
      });
    }
  });
  
  // Find projects
  PROJECTS.forEach(project => {
    if (textLower.includes(project.toLowerCase())) {
      const context = extractContext(text, project);
      entities.push({ 
        type: 'project', 
        name: project, 
        source: sourceName,
        context: context,
      });
    }
  });
  
  // Find questions
  const questions = text.match(/[^.!?\n]+\?/g) || [];
  questions.slice(0, 5).forEach(q => {
    const cleaned = q.trim();
    if (cleaned.length > 20 && cleaned.length < 150) {
      entities.push({ 
        type: 'question', 
        name: cleaned, 
        source: sourceName,
        context: cleaned, // question is its own context
      });
    }
  });
  
  return entities;
}

/**
 * Parse a markdown file
 */
async function parseMarkdownFile(filepath, type = 'memory') {
  try {
    const content = await fs.readFile(filepath, 'utf-8');
    const filename = path.basename(filepath);
    const entities = extractEntitiesWithContext(content, filename);
    
    return {
      filename,
      type,
      content,
      preview: content.slice(0, 300),
      entities,
    };
  } catch (err) {
    return null;
  }
}

/**
 * Build the knowledge graph from workspace files
 */
export async function buildKnowledgeGraph() {
  const nodes = [];
  const edges = [];
  const nodeMap = new Map(); // key -> node id
  const entityContexts = new Map(); // "nodeId:nodeId" -> [contexts]
  
  let nodeId = 0;
  
  const addNode = (name, type, metadata = {}) => {
    const key = `${type}:${name}`;
    if (!nodeMap.has(key)) {
      const id = nodeId++;
      nodeMap.set(key, id);
      nodes.push({
        id,
        name,
        type,
        color: NODE_TYPES[type]?.color || '#888',
        contexts: [], // Will store all thoughts related to this node
        ...metadata,
      });
      return id;
    }
    return nodeMap.get(key);
  };
  
  const addEdge = (sourceId, targetId, relationship, context, source) => {
    const edgeKey = [Math.min(sourceId, targetId), Math.max(sourceId, targetId)].join(':');
    
    const existingEdge = edges.find(e => 
      (e.source === sourceId && e.target === targetId) ||
      (e.source === targetId && e.target === sourceId)
    );
    
    if (existingEdge) {
      // Add to existing edge's contexts
      if (context && !existingEdge.contexts.some(c => c.text === context)) {
        existingEdge.contexts.push({ text: context, source, relationship });
      }
    } else if (sourceId !== targetId) {
      edges.push({ 
        source: sourceId, 
        target: targetId, 
        relationship,
        contexts: context ? [{ text: context, source, relationship }] : [],
      });
    }
    
    // Also add context to the nodes themselves
    if (context) {
      const sourceNode = nodes.find(n => n.id === sourceId);
      const targetNode = nodes.find(n => n.id === targetId);
      
      if (sourceNode && !sourceNode.contexts.some(c => c.text === context)) {
        sourceNode.contexts.push({ text: context, source, connectedTo: targetNode?.name });
      }
      if (targetNode && !targetNode.contexts.some(c => c.text === context)) {
        targetNode.contexts.push({ text: context, source, connectedTo: sourceNode?.name });
      }
    }
  };
  
  // Parse MEMORY.md
  const memoryMd = await parseMarkdownFile(path.join(WORKSPACE, 'MEMORY.md'), 'memory');
  if (memoryMd) {
    const memoryNode = addNode('Long-term Memory', 'memory', { 
      preview: memoryMd.preview,
    });
    
    memoryMd.entities.forEach(entity => {
      const entityNode = addNode(entity.name, entity.type);
      addEdge(memoryNode, entityNode, 'contains', entity.context, entity.source);
    });
    
    // Connect entities that appear in the same paragraph
    const paragraphs = memoryMd.content.split(/\n\n+/);
    paragraphs.forEach(para => {
      const paraEntities = extractEntitiesWithContext(para, 'MEMORY.md');
      for (let i = 0; i < paraEntities.length; i++) {
        for (let j = i + 1; j < paraEntities.length; j++) {
          const e1 = paraEntities[i];
          const e2 = paraEntities[j];
          const id1 = nodeMap.get(`${e1.type}:${e1.name}`);
          const id2 = nodeMap.get(`${e2.type}:${e2.name}`);
          if (id1 !== undefined && id2 !== undefined) {
            addEdge(id1, id2, 'co-occurs', para.slice(0, 200), 'MEMORY.md');
          }
        }
      }
    });
  }
  
  // Parse daily memory files
  const memoryDir = path.join(WORKSPACE, 'memory');
  if (existsSync(memoryDir)) {
    const files = await fs.readdir(memoryDir);
    const mdFiles = files.filter(f => f.match(/^\d{4}-\d{2}-\d{2}\.md$/)).sort().reverse().slice(0, 7);
    
    for (const file of mdFiles) {
      const date = file.replace('.md', '');
      const parsed = await parseMarkdownFile(path.join(memoryDir, file), 'date');
      if (parsed) {
        const dateNode = addNode(date, 'date', { preview: parsed.preview });
        
        parsed.entities.forEach(entity => {
          const entityNode = addNode(entity.name, entity.type);
          addEdge(dateNode, entityNode, 'recorded_on', entity.context, file);
        });
        
        // Connect entities from same day
        const paragraphs = parsed.content.split(/\n\n+/);
        paragraphs.forEach(para => {
          const paraEntities = extractEntitiesWithContext(para, file);
          for (let i = 0; i < paraEntities.length; i++) {
            for (let j = i + 1; j < paraEntities.length; j++) {
              const e1 = paraEntities[i];
              const e2 = paraEntities[j];
              const id1 = nodeMap.get(`${e1.type}:${e1.name}`);
              const id2 = nodeMap.get(`${e2.type}:${e2.name}`);
              if (id1 !== undefined && id2 !== undefined) {
                addEdge(id1, id2, 'co-occurs', para.slice(0, 200), file);
              }
            }
          }
        });
      }
    }
  }
  
  // Parse state.json for current thoughts
  const statePath = path.join(WORKSPACE, 'state.json');
  if (existsSync(statePath)) {
    try {
      const state = JSON.parse(await fs.readFile(statePath, 'utf-8'));
      
      if (state.topOfMind) {
        state.topOfMind.forEach(thought => {
          const thoughtEntities = extractEntitiesWithContext(thought, 'state.json (top of mind)');
          thoughtEntities.forEach(entity => {
            const entityNode = addNode(entity.name, entity.type);
            // Add the thought as context
            const node = nodes.find(n => n.id === entityNode);
            if (node && !node.contexts.some(c => c.text === thought)) {
              node.contexts.push({ text: thought, source: 'Currently thinking about' });
            }
          });
        });
      }
      
      if (state.recentLearnings) {
        state.recentLearnings.forEach(learning => {
          const learnEntities = extractEntitiesWithContext(learning, 'state.json (learnings)');
          learnEntities.forEach(entity => {
            const entityNode = addNode(entity.name, entity.type);
            const node = nodes.find(n => n.id === entityNode);
            if (node && !node.contexts.some(c => c.text === learning)) {
              node.contexts.push({ text: learning, source: 'Recent learning' });
            }
          });
        });
      }
    } catch (err) {
      console.error('Error parsing state.json:', err);
    }
  }
  
  // Calculate node sizes based on connection count
  const connectionCount = new Map();
  edges.forEach(edge => {
    connectionCount.set(edge.source, (connectionCount.get(edge.source) || 0) + 1);
    connectionCount.set(edge.target, (connectionCount.get(edge.target) || 0) + 1);
  });
  
  nodes.forEach(node => {
    node.connections = connectionCount.get(node.id) || 0;
    node.size = Math.max(4, Math.min(20, 4 + node.connections * 2));
    // Limit contexts to most relevant
    node.contexts = node.contexts.slice(0, 10);
    // Add synthesized perspective
    node.perspective = synthesizePerspective(node.name, node.type, node.contexts);
  });
  
  // Add connected nodes info to each node
  nodes.forEach(node => {
    node.connectedNodes = edges
      .filter(e => e.source === node.id || e.target === node.id)
      .map(e => {
        const otherId = e.source === node.id ? e.target : e.source;
        const otherNode = nodes.find(n => n.id === otherId);
        return {
          id: otherId,
          name: otherNode?.name,
          type: otherNode?.type,
          contexts: e.contexts,
        };
      });
  });
  
  return {
    nodes,
    edges,
    stats: {
      totalNodes: nodes.length,
      totalEdges: edges.length,
      nodeTypes: Object.fromEntries(
        Object.keys(NODE_TYPES).map(type => [
          type,
          nodes.filter(n => n.type === type).length
        ])
      ),
    },
    generatedAt: new Date().toISOString(),
  };
}

export default { buildKnowledgeGraph, NODE_TYPES };
