/**
 * Knowledge Graph Generator v2 - LLM-Powered Entity Extraction
 * 
 * Upgrades from hardcoded entity lists to dynamic LLM-based extraction.
 * Uses Claude Sonnet for intelligent entity and relationship discovery.
 */

import fs from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import crypto from 'crypto';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw/workspace');
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN || '7b0823e46d5beef9870db213ace87139542badebad023323';

// Cache directory for LLM extractions (avoid repeated API calls)
const CACHE_DIR = path.join(WORKSPACE, '.cache', 'knowledge-graph');

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
  opinion: { color: '#34d399', label: 'Opinion' },
  realization: { color: '#c084fc', label: 'Realization' },
};

// Relationship types for typed edges
const RELATIONSHIP_TYPES = {
  knows: { label: 'knows', weight: 1.0 },
  works_on: { label: 'works on', weight: 1.2 },
  works_at: { label: 'works at', weight: 1.1 },
  interested_in: { label: 'interested in', weight: 0.8 },
  learned: { label: 'learned', weight: 1.0 },
  questions: { label: 'questions', weight: 0.9 },
  relates_to: { label: 'relates to', weight: 0.5 },
  lives_in: { label: 'lives in', weight: 1.0 },
  family: { label: 'family', weight: 1.5 },
  friend: { label: 'friend', weight: 1.3 },
  roommate: { label: 'roommate', weight: 1.2 },
  mentioned_with: { label: 'mentioned with', weight: 0.3 },
};

/**
 * Initialize cache directory
 */
async function ensureCacheDir() {
  try {
    await fs.mkdir(CACHE_DIR, { recursive: true });
  } catch (err) {
    // Ignore if exists
  }
}

/**
 * Get cache key for text content
 */
function getCacheKey(text) {
  return crypto.createHash('md5').update(text).digest('hex');
}

/**
 * Load cached extraction if available and fresh
 */
async function loadCachedExtraction(cacheKey, maxAgeMs = 3600000) { // 1 hour default
  try {
    const cachePath = path.join(CACHE_DIR, `${cacheKey}.json`);
    const stat = await fs.stat(cachePath);
    const age = Date.now() - stat.mtimeMs;
    
    if (age < maxAgeMs) {
      const data = await fs.readFile(cachePath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    // Cache miss
  }
  return null;
}

/**
 * Save extraction to cache
 */
async function saveCachedExtraction(cacheKey, data) {
  try {
    await ensureCacheDir();
    const cachePath = path.join(CACHE_DIR, `${cacheKey}.json`);
    await fs.writeFile(cachePath, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Cache write error:', err.message);
  }
}

/**
 * Call LLM to extract entities from text
 * Uses Claude Sonnet for intelligent extraction
 */
async function extractEntitiesWithLLM(text, sourceName) {
  // Check cache first
  const cacheKey = getCacheKey(text + sourceName);
  const cached = await loadCachedExtraction(cacheKey);
  if (cached) {
    console.log(`[KG] Cache hit for ${sourceName}`);
    return cached;
  }
  
  // Truncate very long texts
  const truncatedText = text.length > 8000 ? text.slice(0, 8000) + '\n\n[...truncated...]' : text;
  
  const prompt = `Extract entities and relationships from this text. Be thorough but precise.

TEXT SOURCE: ${sourceName}
---
${truncatedText}
---

Extract the following as JSON:

{
  "entities": [
    {
      "name": "entity name (use canonical form, e.g., 'Kartik Krishnan' not just 'Kartik')",
      "type": "person|project|concept|interest|question|opinion|realization|action",
      "context": "brief quote or context where this entity appears (max 150 chars)"
    }
  ],
  "relationships": [
    {
      "from": "entity name",
      "to": "entity name",  
      "type": "knows|works_on|works_at|interested_in|learned|questions|relates_to|lives_in|family|friend|roommate",
      "context": "brief explanation of the relationship"
    }
  ]
}

RULES:
- Extract ALL people mentioned by name
- Extract projects, companies, tools, and technologies as concepts or projects
- Extract explicit questions (ending in ?) as question type
- Extract opinions ("I think...", "I believe...") as opinion type
- Extract realizations ("I realized...", "figured out...") as realization type
- For relationships, only include those clearly stated or strongly implied
- Don't infer relationships that aren't supported by the text
- Keep context quotes SHORT but meaningful

Return ONLY valid JSON, no explanation.`;

  try {
    const response = await fetch(`${OPENCLAW_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENCLAW_TOKEN}`,
      },
      body: JSON.stringify({
        model: 'anthropic/claude-opus-4-5',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2000,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || '';
      
      // Parse JSON from response (handle markdown code blocks)
      let jsonStr = content;
      const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (jsonMatch) {
        jsonStr = jsonMatch[1];
      }
      
      try {
        const extracted = JSON.parse(jsonStr.trim());
        
        // Validate structure
        if (!extracted.entities) extracted.entities = [];
        if (!extracted.relationships) extracted.relationships = [];
        
        // Add source to all entities
        extracted.entities = extracted.entities.map(e => ({
          ...e,
          source: sourceName,
        }));
        
        extracted.relationships = extracted.relationships.map(r => ({
          ...r,
          source: sourceName,
        }));
        
        // Cache the result
        await saveCachedExtraction(cacheKey, extracted);
        
        console.log(`[KG] Extracted ${extracted.entities.length} entities, ${extracted.relationships.length} relationships from ${sourceName}`);
        return extracted;
        
      } catch (parseErr) {
        console.error(`[KG] JSON parse error for ${sourceName}:`, parseErr.message);
        console.error('Raw content:', content.slice(0, 500));
      }
    } else {
      const errText = await response.text();
      console.error(`[KG] LLM error for ${sourceName}:`, response.status, errText.slice(0, 200));
    }
  } catch (err) {
    console.error(`[KG] Extraction failed for ${sourceName}:`, err.message);
  }
  
  // Return empty on failure
  return { entities: [], relationships: [] };
}

/**
 * Generate a GENUINE perspective by calling the LLM
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
        model: 'anthropic/claude-opus-4-5',
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

/**
 * Extract context snippet around a term
 */
function extractContext(text, term, charsBefore = 50, charsAfter = 100) {
  const idx = text.toLowerCase().indexOf(term.toLowerCase());
  if (idx === -1) return null;
  
  const start = Math.max(0, idx - charsBefore);
  const end = Math.min(text.length, idx + term.length + charsAfter);
  
  let snippet = text.slice(start, end).trim();
  if (start > 0) snippet = '...' + snippet.replace(/^\S*\s/, '');
  if (end < text.length) snippet = snippet.replace(/\s\S*$/, '') + '...';
  
  return snippet;
}

/**
 * Synthesize perspective from contexts (fallback when LLM not available)
 */
function synthesizePerspective(name, type, contexts) {
  if (!contexts || contexts.length === 0) return null;
  
  const connectionCount = contexts.length;
  const sources = [...new Set(contexts.map(c => c.source))];
  
  const paragraphs = [];
  
  if (connectionCount > 5) {
    paragraphs.push(`Appears frequently — ${connectionCount} traces across ${sources.length} sources.`);
  }
  
  if (contexts[0]?.text) {
    paragraphs.push(contexts[0].text.slice(0, 200));
  }
  
  return {
    synthesis: paragraphs.join(' '),
    insights: contexts.slice(0, 3).map(c => c.text?.slice(0, 100)),
    meta: {
      traces: connectionCount,
      sources: sources.length,
    }
  };
}

/**
 * Parse a markdown file and extract entities using LLM
 */
async function parseMarkdownFile(filepath, type = 'memory') {
  try {
    const content = await fs.readFile(filepath, 'utf-8');
    const filename = path.basename(filepath);
    
    // Use LLM extraction
    const extracted = await extractEntitiesWithLLM(content, filename);
    
    return {
      filename,
      type,
      content,
      preview: content.slice(0, 300),
      entities: extracted.entities,
      relationships: extracted.relationships,
    };
  } catch (err) {
    console.error(`Error parsing ${filepath}:`, err.message);
    return null;
  }
}

/**
 * Build the knowledge graph from workspace files
 */
export async function buildKnowledgeGraph() {
  console.log('[KG] Building knowledge graph with LLM extraction...');
  
  const nodes = [];
  const edges = [];
  const nodeMap = new Map(); // key -> node id
  
  let nodeId = 0;
  
  const addNode = (name, type, metadata = {}) => {
    // Normalize name
    const normalizedName = name.trim();
    const key = `${type}:${normalizedName.toLowerCase()}`;
    
    if (!nodeMap.has(key)) {
      const id = nodeId++;
      nodeMap.set(key, id);
      nodes.push({
        id,
        name: normalizedName,
        type,
        color: NODE_TYPES[type]?.color || '#888',
        contexts: [],
        ...metadata,
      });
      return id;
    }
    return nodeMap.get(key);
  };
  
  const getNodeId = (name, type) => {
    const key = `${type}:${name.toLowerCase().trim()}`;
    return nodeMap.get(key);
  };
  
  const addEdge = (sourceId, targetId, relationship, context, source) => {
    if (sourceId === undefined || targetId === undefined || sourceId === targetId) return;
    
    const existingEdge = edges.find(e => 
      (e.source === sourceId && e.target === targetId) ||
      (e.source === targetId && e.target === sourceId)
    );
    
    const relType = RELATIONSHIP_TYPES[relationship] || RELATIONSHIP_TYPES.relates_to;
    
    if (existingEdge) {
      if (context && !existingEdge.contexts.some(c => c.text === context)) {
        existingEdge.contexts.push({ text: context, source, relationship });
      }
      // Upgrade relationship type if stronger
      if (relType.weight > (RELATIONSHIP_TYPES[existingEdge.relationship]?.weight || 0)) {
        existingEdge.relationship = relationship;
      }
    } else {
      edges.push({ 
        source: sourceId, 
        target: targetId, 
        relationship,
        weight: relType.weight,
        contexts: context ? [{ text: context, source, relationship }] : [],
      });
    }
    
    // Add context to nodes
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
    const memoryNode = addNode('Long-term Memory', 'memory', { preview: memoryMd.preview });
    
    // Add entities from LLM extraction
    for (const entity of memoryMd.entities) {
      const entityNode = addNode(entity.name, entity.type);
      addEdge(memoryNode, entityNode, 'contains', entity.context, entity.source);
    }
    
    // Add relationships from LLM extraction
    for (const rel of memoryMd.relationships) {
      // Find or create the nodes
      const fromEntity = memoryMd.entities.find(e => 
        e.name.toLowerCase() === rel.from.toLowerCase()
      );
      const toEntity = memoryMd.entities.find(e => 
        e.name.toLowerCase() === rel.to.toLowerCase()
      );
      
      if (fromEntity && toEntity) {
        const fromId = getNodeId(fromEntity.name, fromEntity.type);
        const toId = getNodeId(toEntity.name, toEntity.type);
        if (fromId !== undefined && toId !== undefined) {
          addEdge(fromId, toId, rel.type, rel.context, rel.source);
        }
      }
    }
  }
  
  // Parse SOUL.md for identity concepts
  const soulMd = await parseMarkdownFile(path.join(WORKSPACE, 'SOUL.md'), 'memory');
  if (soulMd) {
    const soulNode = addNode('Core Identity', 'memory', { preview: soulMd.preview });
    
    for (const entity of soulMd.entities) {
      const entityNode = addNode(entity.name, entity.type);
      addEdge(soulNode, entityNode, 'defines', entity.context, entity.source);
    }
    
    for (const rel of soulMd.relationships) {
      const fromEntity = soulMd.entities.find(e => e.name.toLowerCase() === rel.from.toLowerCase());
      const toEntity = soulMd.entities.find(e => e.name.toLowerCase() === rel.to.toLowerCase());
      if (fromEntity && toEntity) {
        const fromId = getNodeId(fromEntity.name, fromEntity.type);
        const toId = getNodeId(toEntity.name, toEntity.type);
        if (fromId !== undefined && toId !== undefined) {
          addEdge(fromId, toId, rel.type, rel.context, rel.source);
        }
      }
    }
  }
  
  // Parse daily memory files (last 7 days)
  const memoryDir = path.join(WORKSPACE, 'memory');
  if (existsSync(memoryDir)) {
    const files = await fs.readdir(memoryDir);
    const mdFiles = files.filter(f => f.match(/^\d{4}-\d{2}-\d{2}\.md$/)).sort().reverse().slice(0, 7);
    
    for (const file of mdFiles) {
      const date = file.replace('.md', '');
      const parsed = await parseMarkdownFile(path.join(memoryDir, file), 'date');
      
      if (parsed) {
        const dateNode = addNode(date, 'date', { preview: parsed.preview });
        
        for (const entity of parsed.entities) {
          const entityNode = addNode(entity.name, entity.type);
          addEdge(dateNode, entityNode, 'recorded_on', entity.context, file);
        }
        
        for (const rel of parsed.relationships) {
          const fromEntity = parsed.entities.find(e => e.name.toLowerCase() === rel.from.toLowerCase());
          const toEntity = parsed.entities.find(e => e.name.toLowerCase() === rel.to.toLowerCase());
          if (fromEntity && toEntity) {
            const fromId = getNodeId(fromEntity.name, fromEntity.type);
            const toId = getNodeId(toEntity.name, toEntity.type);
            if (fromId !== undefined && toId !== undefined) {
              addEdge(fromId, toId, rel.type, rel.context, rel.source);
            }
          }
        }
      }
    }
  }
  
  // Parse state.json for current thoughts
  const statePath = path.join(WORKSPACE, 'state.json');
  if (existsSync(statePath)) {
    try {
      const state = JSON.parse(await fs.readFile(statePath, 'utf-8'));
      const stateText = [
        state.topOfMind?.join('\n'),
        state.recentLearnings?.join('\n'),
        state.questionsOnMyMind?.join('\n'),
      ].filter(Boolean).join('\n\n');
      
      if (stateText) {
        const stateExtracted = await extractEntitiesWithLLM(stateText, 'state.json (current thoughts)');
        
        for (const entity of stateExtracted.entities) {
          const entityNode = addNode(entity.name, entity.type);
          const node = nodes.find(n => n.id === entityNode);
          if (node && entity.context) {
            node.contexts.push({ text: entity.context, source: 'Currently thinking about' });
          }
        }
      }
    } catch (err) {
      console.error('Error parsing state.json:', err.message);
    }
  }
  
  // Calculate node sizes based on connection count
  const connectionCount = new Map();
  edges.forEach(edge => {
    connectionCount.set(edge.source, (connectionCount.get(edge.source) || 0) + (edge.weight || 1));
    connectionCount.set(edge.target, (connectionCount.get(edge.target) || 0) + (edge.weight || 1));
  });
  
  nodes.forEach(node => {
    node.connections = connectionCount.get(node.id) || 0;
    node.size = Math.max(4, Math.min(20, 4 + node.connections * 1.5));
    node.contexts = node.contexts.slice(0, 10);
    node.perspective = synthesizePerspective(node.name, node.type, node.contexts);
  });
  
  // Add connected nodes info
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
          relationship: e.relationship,
          contexts: e.contexts,
        };
      });
  });
  
  console.log(`[KG] Built graph: ${nodes.length} nodes, ${edges.length} edges`);
  
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
      relationshipTypes: Object.fromEntries(
        [...new Set(edges.map(e => e.relationship))].map(rel => [
          rel,
          edges.filter(e => e.relationship === rel).length
        ])
      ),
    },
    generatedAt: new Date().toISOString(),
    version: '2.0-llm',
  };
}

/**
 * Clear the extraction cache (call when memory files change significantly)
 */
export async function clearCache() {
  try {
    const files = await fs.readdir(CACHE_DIR);
    for (const file of files) {
      await fs.unlink(path.join(CACHE_DIR, file));
    }
    console.log(`[KG] Cleared ${files.length} cached extractions`);
  } catch (err) {
    // Cache dir may not exist
  }
}

export default { buildKnowledgeGraph, clearCache, NODE_TYPES, RELATIONSHIP_TYPES };
