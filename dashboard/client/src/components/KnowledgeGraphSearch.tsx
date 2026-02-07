import { useState } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';
import { getAuth } from '../lib/api';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:3001';

interface SearchResult {
  query: string;
  interpretation?: string;
  answer: string;
  confidence: 'high' | 'medium' | 'low';
  relevantNodes?: Array<{
    name: string;
    type: string;
    relevance: string;
  }>;
  paths?: Array<{
    description: string;
    nodes: string[];
  }>;
  graphStats?: {
    totalNodes: number;
    totalEdges: number;
  };
}

const confidenceColors = {
  high: 'text-green-400',
  medium: 'text-yellow-400',
  low: 'text-red-400',
};

export default function KnowledgeGraphSearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const auth = getAuth();
      const res = await fetch(`${API_BASE}/api/knowledge-graph/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Basic ${auth}`,
        },
        body: JSON.stringify({ query: query.trim() }),
      });
      
      if (!res.ok) {
        throw new Error('Search failed');
      }
      
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleSearch();
    }
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about my mind... (e.g., 'What is Limen interested in?')"
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pl-11 text-white placeholder-white/30 focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/20"
          disabled={loading}
        />
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm text-white/70 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              Thinking...
            </>
          ) : (
            <>
              <Sparkles className="w-3 h-3" />
              Search
            </>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4 animate-in fade-in duration-300">
          {/* Answer */}
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium text-white/70">Answer</span>
              <span className={`text-xs px-2 py-0.5 rounded-full bg-white/5 ${confidenceColors[result.confidence]}`}>
                {result.confidence} confidence
              </span>
            </div>
            <p className="text-white/90 leading-relaxed whitespace-pre-wrap">
              {result.answer}
            </p>
          </div>

          {/* Relevant Nodes */}
          {result.relevantNodes && result.relevantNodes.length > 0 && (
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <h4 className="text-sm font-medium text-white/70 mb-3">Relevant Nodes</h4>
              <div className="space-y-2">
                {result.relevantNodes.map((node, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <span className="px-2 py-0.5 bg-white/10 rounded text-white/50 text-xs shrink-0">
                      {node.type}
                    </span>
                    <div>
                      <span className="text-white/80 font-medium">{node.name}</span>
                      {node.relevance && (
                        <p className="text-white/50 text-xs mt-0.5">{node.relevance}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Paths */}
          {result.paths && result.paths.length > 0 && (
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <h4 className="text-sm font-medium text-white/70 mb-3">Paths Found</h4>
              <div className="space-y-3">
                {result.paths.map((path, i) => (
                  <div key={i} className="text-sm">
                    <p className="text-white/60 mb-1">{path.description}</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      {path.nodes.map((node, j) => (
                        <span key={j} className="flex items-center gap-1">
                          <span className="px-2 py-1 bg-white/10 rounded text-white/70 text-xs">
                            {node}
                          </span>
                          {j < path.nodes.length - 1 && (
                            <span className="text-white/30">→</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Graph Stats */}
          {result.graphStats && (
            <div className="text-xs text-white/30 text-center">
              Searched {result.graphStats.totalNodes} nodes and {result.graphStats.totalEdges} edges
            </div>
          )}
        </div>
      )}

      {/* Example queries */}
      {!result && !loading && (
        <div className="text-xs text-white/30">
          <span className="text-white/50">Try:</span>{' '}
          <button onClick={() => setQuery("What is Limen interested in?")} className="hover:text-white/50 underline">
            What is Limen interested in?
          </button>
          {' · '}
          <button onClick={() => setQuery("Who does Kartik work with?")} className="hover:text-white/50 underline">
            Who does Kartik work with?
          </button>
          {' · '}
          <button onClick={() => setQuery("What has Limen learned recently?")} className="hover:text-white/50 underline">
            What has Limen learned recently?
          </button>
        </div>
      )}
    </div>
  );
}
