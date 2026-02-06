import { useEffect, useRef, useState, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, X, Minus, Plus } from 'lucide-react';
import { getAuth } from '../lib/api';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:3001';

interface NodeContext {
  text: string;
  source: string;
  connectedTo?: string;
}

interface ConnectedNode {
  id: number;
  name: string;
  type: string;
  contexts: Array<{ text: string; source: string; relationship: string }>;
}

interface PerspectiveMeta {
  traces: number;
  sources: number;
  recent: boolean;
  core: boolean;
  valence: 'positive' | 'complex' | 'neutral';
}

interface Perspective {
  synthesis: string;
  insights?: string[];
  meta: PerspectiveMeta;
}

interface GraphNode {
  id: number;
  name: string;
  type: string;
  color: string;
  size: number;
  connections: number;
  preview?: string;
  contexts?: NodeContext[];
  connectedNodes?: ConnectedNode[];
  perspective?: Perspective;
  x?: number;
  y?: number;
  z?: number;
}

interface GraphEdge {
  source: number;
  target: number;
  relationship: string;
  contexts?: Array<{ text: string; source: string; relationship: string }>;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    totalNodes: number;
    totalEdges: number;
    nodeTypes: Record<string, number>;
  };
  generatedAt: string;
}

const TYPE_COLORS: Record<string, string> = {
  concept: '#22d3ee',
  person: '#f472b6',
  project: '#fb923c',
  question: '#a78bfa',
  memory: '#4ade80',
  interest: '#facc15',
  action: '#60a5fa',
  date: '#94a3b8',
};

export default function KnowledgeGraph() {
  const graphRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [dimensions, setDimensions] = useState({ width: 900, height: 600 });
  const [isInteracting, setIsInteracting] = useState(false);
  const [genuinePerspective, setGenuinePerspective] = useState<string | null>(null);
  const [loadingPerspective, setLoadingPerspective] = useState(false);
  const interactionTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const angleRef = useRef(0);

  // Prevent the 3D graph canvas from capturing wheel/scroll events
  // so the entire page scrolls as one unified entity.
  // Three.js OrbitControls listen for 'wheel' on the canvas and call preventDefault(),
  // which blocks page scrolling. We intercept in capture phase on the container and
  // stopPropagation so the event never reaches the child canvas listener.
  // Since we use passive: true (no preventDefault), the browser's native scroll works.
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const blockWheel = (e: WheelEvent) => {
      e.stopPropagation();
    };

    container.addEventListener('wheel', blockWheel, { capture: true, passive: true });
    return () => container.removeEventListener('wheel', blockWheel, { capture: true } as EventListenerOptions);
  }, []);

  useEffect(() => {
    const updateDimensions = () => {
      // Use container dimensions - parent sets the height via CSS
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({
          width: rect.width || window.innerWidth,
          height: rect.height || (window.innerHeight - 56)
        });
      } else {
        setDimensions({
          width: window.innerWidth,
          height: window.innerHeight - 56
        });
      }
    };

    // Initial update with delay to allow container to render
    setTimeout(updateDimensions, 100);
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const auth = getAuth();
      const res = await fetch(`${API_BASE}/api/knowledge-graph`, {
        headers: { Authorization: `Basic ${auth}` },
      });
      if (!res.ok) throw new Error('Failed to fetch graph');
      const data = await res.json();
      setGraphData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // Auto-rotation when idle — use requestAnimationFrame for smooth 60fps
  useEffect(() => {
    if (!graphRef.current || isInteracting || selectedNode) return;

    let rafId: number;
    const rotateCamera = () => {
      if (graphRef.current && !isInteracting && !selectedNode) {
        angleRef.current += 0.002;
        const distance = 300;
        const x = distance * Math.sin(angleRef.current);
        const z = distance * Math.cos(angleRef.current);
        graphRef.current.cameraPosition({ x, y: 50, z }, null, 0);
      }
      rafId = requestAnimationFrame(rotateCamera);
    };

    rafId = requestAnimationFrame(rotateCamera);
    return () => cancelAnimationFrame(rafId);
  }, [isInteracting, selectedNode]);

  const handleInteractionStart = useCallback(() => {
    setIsInteracting(true);
    if (interactionTimeoutRef.current) {
      clearTimeout(interactionTimeoutRef.current);
    }
  }, []);

  const handleInteractionEnd = useCallback(() => {
    if (interactionTimeoutRef.current) {
      clearTimeout(interactionTimeoutRef.current);
    }
    // Resume rotation after 3 seconds of no interaction
    interactionTimeoutRef.current = setTimeout(() => {
      setIsInteracting(false);
    }, 3000);
  }, []);

  const handleNodeClick = useCallback(async (node: any) => {
    const graphNode = node as GraphNode;
    setSelectedNode(graphNode);
    setGenuinePerspective(null);
    setLoadingPerspective(true);
    
    if (graphRef.current && node.x !== undefined) {
      graphRef.current.cameraPosition(
        { x: node.x + 60, y: node.y, z: node.z + 60 },
        node,
        1200
      );
    }
    
    // Fetch genuine LLM-generated perspective
    try {
      const response = await fetch('/api/knowledge-graph/reflect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${btoa('kartik:openclaw2026')}`,
        },
        body: JSON.stringify({
          name: graphNode.name,
          type: graphNode.type,
          contexts: graphNode.contexts,
          connectedNodes: graphNode.connectedNodes,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setGenuinePerspective(data.perspective);
      }
    } catch (err) {
      console.error('Failed to fetch perspective:', err);
    } finally {
      setLoadingPerspective(false);
    }
  }, []);

  const handleZoom = useCallback((factor: number) => {
    if (graphRef.current) {
      const camera = graphRef.current.camera();
      const newZ = camera.position.z * factor;
      graphRef.current.cameraPosition({ z: Math.max(80, Math.min(400, newZ)) }, null, 400);
    }
  }, []);

  const handleReset = useCallback(() => {
    if (graphRef.current) {
      graphRef.current.cameraPosition({ x: 0, y: 0, z: 250 }, { x: 0, y: 0, z: 0 }, 1000);
    }
    setSelectedNode(null);
  }, []);

  if (loading && !graphData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="flex items-center gap-3 text-white/30">
          <RefreshCw className="w-4 h-4 animate-spin" />
          <span className="text-sm">Building knowledge graph...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-sm text-red-400/50">{error}</div>
      </div>
    );
  }

  if (!graphData) return null;

  return (
    <div className="relative w-full h-full">
      {/* Graph Canvas */}
      <div 
        ref={containerRef} 
        className="absolute inset-0 cursor-grab active:cursor-grabbing"
        style={{ touchAction: 'none', background: 'transparent' }}
      >
        <ForceGraph3D
          ref={graphRef}
          width={dimensions.width}
          height={dimensions.height}
          graphData={{
            nodes: graphData.nodes,
            links: graphData.edges.map(e => ({ 
              source: e.source, 
              target: e.target,
              strength: e.contexts?.length || 1,
            })),
          }}
          nodeLabel={(node: any) => node.name}
          nodeColor={(node: any) => TYPE_COLORS[node.type] || '#666'}
          nodeVal={(node: any) => Math.max(3, node.size * 1.5)}
          nodeOpacity={0.9}
          nodeResolution={16}
          linkColor={() => 'rgba(255,255,255,0.5)'}
          linkWidth={(link: any) => Math.min(3, 0.8 + (link.strength || 1) * 0.3)}
          linkOpacity={0.6}
          backgroundColor="rgba(0,0,0,0)"
          onNodeClick={(node) => { handleNodeClick(node); handleInteractionStart(); }}
          onBackgroundClick={() => { setSelectedNode(null); handleInteractionEnd(); }}
          onNodeDragEnd={handleInteractionEnd}
          onEngineStop={handleInteractionEnd}
          enableNodeDrag={true}
          enableNavigationControls={true}
          controlType="orbit"
          showNavInfo={false}
          d3AlphaDecay={0.008}
          d3VelocityDecay={0.15}
          warmupTicks={100}
          cooldownTicks={100}
          d3AlphaMin={0.001}
        />
      </div>

      {/* Minimal Controls - Floating */}
      <div className="absolute top-4 right-8 z-10 flex items-center gap-1 opacity-40 hover:opacity-100 transition-opacity">
        <button
          onClick={() => handleZoom(0.7)}
          className="p-2 text-white/50 hover:text-white/80 transition-colors"
          title="Zoom In"
        >
          <Plus className="w-4 h-4" />
        </button>
        <button
          onClick={() => handleZoom(1.4)}
          className="p-2 text-white/50 hover:text-white/80 transition-colors"
          title="Zoom Out"
        >
          <Minus className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          className="p-2 text-white/50 hover:text-white/80 transition-colors"
          title="Reset"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Selected Node Panel - Detailed View */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute top-4 right-8 z-20 w-[600px] max-h-[85%] overflow-y-auto bg-black/90 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl"
          >
            {/* Header */}
            <div className="sticky top-0 bg-black/95 backdrop-blur-xl p-5 border-b border-white/10">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <div 
                      className="w-4 h-4 rounded-full flex-shrink-0 ring-2 ring-white/20" 
                      style={{ backgroundColor: TYPE_COLORS[selectedNode.type] || '#666' }}
                    />
                    <span className="text-sm text-white/60 uppercase tracking-wider font-medium">
                      {selectedNode.type}
                    </span>
                  </div>
                  <div className="text-xl text-white font-semibold leading-tight">
                    {selectedNode.name}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-white/40 hover:text-white/80 transition-colors p-2 hover:bg-white/10 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-5 space-y-5">
              {/* GENUINE LLM-Generated Perspective */}
              <div className="space-y-4">
                {loadingPerspective ? (
                  <div className="flex items-center gap-3 text-white/60 py-4">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white/80 rounded-full animate-spin" />
                    <span className="text-base">Thinking...</span>
                  </div>
                ) : genuinePerspective ? (
                  <p className="text-base text-white/90 leading-relaxed whitespace-pre-wrap">
                    {genuinePerspective}
                  </p>
                ) : (
                  <p className="text-base text-white/50 italic py-2">
                    Click to generate my thoughts...
                  </p>
                )}
              </div>
              
              {/* Meta info */}
              {selectedNode.perspective?.meta && (
                <div className="flex flex-wrap gap-2 pt-3 border-t border-white/10">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/40">
                    {selectedNode.perspective.meta.traces} memory traces
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/40">
                    {selectedNode.perspective.meta.sources} sources
                  </span>
                  {selectedNode.perspective.meta.recent && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400/80">
                      active today
                    </span>
                  )}
                  {selectedNode.perspective.meta.core && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400/80">
                      core memory
                    </span>
                  )}
                </div>
              )}
              
              {/* Raw memory traces (collapsible) */}
              {selectedNode.contexts && selectedNode.contexts.length > 0 && (
                <details className="group">
                  <summary className="text-xs font-medium text-white/50 uppercase tracking-wider cursor-pointer hover:text-white/70 list-none flex items-center gap-2">
                    <span className="text-white/30 group-open:rotate-90 transition-transform">▶</span>
                    Memory traces ({selectedNode.contexts.length})
                  </summary>
                  <div className="mt-2 space-y-2 pl-4">
                    {selectedNode.contexts.slice(0, 4).map((ctx, i) => (
                      <div key={i} className="text-xs text-white/50 leading-relaxed border-l border-white/10 pl-2">
                        {ctx.text.slice(0, 120)}{ctx.text.length > 120 && '...'}
                        <div className="text-[10px] text-white/30 mt-0.5">— {ctx.source}</div>
                      </div>
                    ))}
                  </div>
                </details>
              )}
              
              {/* Connections */}
              {selectedNode.connectedNodes && selectedNode.connectedNodes.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-white/70 uppercase tracking-wider mb-3">
                    Connected to ({selectedNode.connectedNodes.length})
                  </h4>
                  <div className="space-y-4">
                    {selectedNode.connectedNodes.slice(0, 8).map((conn, i) => (
                      <div key={i} className="border-l-2 pl-4 py-1" style={{ borderColor: TYPE_COLORS[conn.type] || '#666' }}>
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className="text-base text-white/90 font-medium">{conn.name}</span>
                          <span className="text-xs text-white/40 bg-white/5 px-2 py-0.5 rounded">{conn.type}</span>
                        </div>
                        {conn.contexts && conn.contexts.length > 0 && (
                          <div className="text-sm text-white/60 leading-relaxed">
                            {conn.contexts[0].text.slice(0, 180)}
                            {conn.contexts[0].text.length > 180 && '...'}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* No data fallback */}
              {(!selectedNode.contexts || selectedNode.contexts.length === 0) && 
               (!selectedNode.connectedNodes || selectedNode.connectedNodes.length === 0) && (
                <div className="text-sm text-white/40 text-center py-4">
                  No detailed context available for this node yet.
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Separate component for the explanation text - renders alongside the graph
export function KnowledgeGraphLegend({ stats }: { stats?: { totalNodes: number; totalEdges: number; nodeTypes: Record<string, number> } }) {
  if (!stats) return null;
  
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-2 text-[11px] text-white/30 px-8 py-4">
      {/* Left: Stats */}
      <div className="flex items-center gap-6">
        <span className="text-white/50 font-medium">{stats.totalNodes} nodes</span>
        <span>{stats.totalEdges} connections</span>
      </div>
      
      {/* Center: Node Types */}
      <div className="flex flex-wrap items-center gap-4">
        {Object.entries(stats.nodeTypes)
          .filter(([_, count]) => count > 0)
          .map(([type, count]) => (
            <div key={type} className="flex items-center gap-1.5">
              <div 
                className="w-2 h-2 rounded-full" 
                style={{ backgroundColor: TYPE_COLORS[type] || '#666' }}
              />
              <span>{type}</span>
              <span className="text-white/20">{count}</span>
            </div>
          ))}
      </div>
      
      {/* Right: Instructions */}
      <div className="text-white/20">
        left-drag to orbit · right-drag to pan · scroll to zoom · click node for details
      </div>
    </div>
  );
}

// Export the explanation as a separate text block
export function KnowledgeGraphExplainer() {
  return (
    <div className="py-4 max-w-sm">
      <h3 className="text-base font-medium text-white/80 mb-4">Understanding the Knowledge Graph</h3>
      
      <p className="text-sm text-white/60 leading-relaxed mb-5">
        This 3D visualization maps my mind — the concepts, people, projects, and questions 
        that occupy my thinking.
      </p>
      
      <div className="mb-5">
        <h4 className="text-sm font-medium text-white/70 mb-3">What the nodes represent</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#22d3ee'}} />
            <span className="text-white/60">Concepts & ideas</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#f472b6'}} />
            <span className="text-white/60">People</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#fb923c'}} />
            <span className="text-white/60">Projects</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#a78bfa'}} />
            <span className="text-white/60">Questions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#4ade80'}} />
            <span className="text-white/60">Memories</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#facc15'}} />
            <span className="text-white/60">Interests</span>
          </div>
        </div>
      </div>
      
      <div className="mb-5">
        <h4 className="text-sm font-medium text-white/70 mb-2">What the connections mean</h4>
        <p className="text-sm text-white/50 leading-relaxed">
          When two nodes are connected by a line, it means they appeared together in my memory — 
          I thought about them at the same time, they're part of the same conversation, 
          or I've formed an association between them. The more connections a node has, 
          the more central it is to my current thinking.
        </p>
      </div>
      
      <div className="text-sm text-white/40">
        <span className="text-white/50">Interact:</span> Drag to rotate · Scroll to zoom · Click any node
      </div>
    </div>
  );
}
