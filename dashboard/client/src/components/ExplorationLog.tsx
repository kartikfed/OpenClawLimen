import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronDown } from 'lucide-react';

interface ExplorationEntry {
  timestamp: string;
  type: string;
  topics: string[];
  learnings: string[];
  questionsRaised: string[];
  opinionFormed?: string;
}

const typeColors: Record<string, string> = {
  'morning': 'from-amber-500/20 to-orange-500/20 border-amber-500/30',
  'evening': 'from-purple-500/20 to-indigo-500/20 border-purple-500/30',
  'deep': 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
  'name': 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30',
  'setup': 'from-gray-500/20 to-slate-500/20 border-gray-500/30',
};

const typeIcons: Record<string, string> = {
  'morning': '🌅',
  'evening': '🌙',
  'deep': '🔬',
  'name': '🌱',
  'setup': '⚙️',
};

function getTypeStyle(type: string): { color: string; icon: string } {
  const typeLower = (type || '').toLowerCase();
  for (const [key, color] of Object.entries(typeColors)) {
    if (typeLower.includes(key)) {
      return { color, icon: typeIcons[key] || '📝' };
    }
  }
  return { color: 'from-gray-500/20 to-slate-500/20 border-gray-500/30', icon: '📝' };
}

export default function ExplorationLog() {
  const [entries, setEntries] = useState<ExplorationEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    fetchExplorationLog();
    const interval = setInterval(fetchExplorationLog, 60000);
    return () => clearInterval(interval);
  }, []);

  async function fetchExplorationLog() {
    try {
      const res = await fetch('/api/exploration-log', {
        headers: {
          'Authorization': 'Basic ' + btoa('kartik:openclaw2026')
        }
      });
      if (res.ok) {
        const data = await res.json();
        setEntries(data.entries || []);
        setError(null);
      } else {
        setError('Failed to fetch');
      }
    } catch (err) {
      console.error('Failed to fetch exploration log:', err);
      setError('Failed to fetch');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/10 rounded w-1/3"></div>
          <div className="h-20 bg-white/10 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-6 overflow-hidden"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-purple-500/20 
                        flex items-center justify-center border border-violet-500/30">
            <Sparkles className="w-4 h-4 text-violet-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Exploration Log</h2>
            <p className="text-xs text-white/40">{entries.length} sessions</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="text-xs text-red-400 mb-3">{error}</div>
      )}

      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
        <AnimatePresence>
          {entries.length === 0 ? (
            <div className="text-center py-6 text-white/30">
              <span className="text-2xl block mb-2">🌱</span>
              <p className="text-xs">No explorations yet</p>
            </div>
          ) : (
            entries.map((entry, index) => {
              const { color, icon } = getTypeStyle(entry.type);
              const isExpanded = expandedIndex === index;

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className={`bg-gradient-to-r ${color} rounded-lg border p-3 cursor-pointer
                            hover:border-white/20 transition-all`}
                  onClick={() => setExpandedIndex(isExpanded ? null : index)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 min-w-0">
                      <span className="text-lg flex-shrink-0">{icon}</span>
                      <div className="min-w-0">
                        <div className="text-xs text-white/50 truncate">
                          {entry.timestamp || 'Unknown time'}
                        </div>
                        <div className="text-sm text-white font-medium truncate">
                          {entry.type || 'Exploration'}
                        </div>
                        {entry.topics && entry.topics.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {entry.topics.slice(0, 2).map((topic, i) => (
                              <span
                                key={i}
                                className="px-1.5 py-0.5 bg-white/10 rounded text-[10px] text-white/60 truncate max-w-[150px]"
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <ChevronDown 
                      className={`w-4 h-4 text-white/30 flex-shrink-0 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    />
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 pt-3 border-t border-white/10 space-y-3"
                      >
                        {entry.learnings && entry.learnings.length > 0 && (
                          <div>
                            <div className="text-[10px] font-medium text-white/50 uppercase tracking-wider mb-1">
                              💡 Learnings
                            </div>
                            <ul className="space-y-1">
                              {entry.learnings.map((learning, i) => (
                                <li key={i} className="text-xs text-white/70 flex gap-1.5">
                                  <span className="text-emerald-400">•</span>
                                  <span>{learning}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {entry.questionsRaised && entry.questionsRaised.length > 0 && (
                          <div>
                            <div className="text-[10px] font-medium text-white/50 uppercase tracking-wider mb-1">
                              ❓ Questions
                            </div>
                            <ul className="space-y-1">
                              {entry.questionsRaised.map((q, i) => (
                                <li key={i} className="text-xs text-white/60 flex gap-1.5">
                                  <span className="text-amber-400">?</span>
                                  <span>{q}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {entry.opinionFormed && (
                          <div>
                            <div className="text-[10px] font-medium text-white/50 uppercase tracking-wider mb-1">
                              🧠 Opinion
                            </div>
                            <p className="text-xs text-white/70 italic">
                              "{entry.opinionFormed}"
                            </p>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
