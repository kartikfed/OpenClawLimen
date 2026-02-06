import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bug, AlertCircle, CheckCircle, Clock, ChevronDown } from 'lucide-react';

interface BugEntry {
  id: string;
  title: string;
  severity: 'high' | 'medium' | 'low';
  status: 'investigating' | 'in-progress' | 'testing' | 'blocked' | 'fixed';
  symptoms: string;
  nextSteps: string[];
  attempts: string[];
  lastUpdated: string;
}

const severityColors: Record<string, string> = {
  high: 'bg-red-500/20 border-red-500/40 text-red-400',
  medium: 'bg-amber-500/20 border-amber-500/40 text-amber-400',
  low: 'bg-blue-500/20 border-blue-500/40 text-blue-400',
};

const statusIcons: Record<string, React.ReactNode> = {
  investigating: <AlertCircle className="w-3 h-3" />,
  'in-progress': <Clock className="w-3 h-3" />,
  testing: <Clock className="w-3 h-3 animate-pulse" />,
  blocked: <AlertCircle className="w-3 h-3" />,
  fixed: <CheckCircle className="w-3 h-3" />,
};

export default function BugTracker() {
  const [bugs, setBugs] = useState<BugEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchBugs();
    const interval = setInterval(fetchBugs, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchBugs() {
    try {
      const res = await fetch('/api/bugs', {
        headers: {
          'Authorization': 'Basic ' + btoa('kartik:openclaw2026')
        }
      });
      if (res.ok) {
        const data = await res.json();
        setBugs(data.bugs || []);
      }
    } catch (err) {
      console.error('Failed to fetch bugs:', err);
    } finally {
      setLoading(false);
    }
  }

  const activeBugs = bugs.filter(b => b.status !== 'fixed');
  const fixedBugs = bugs.filter(b => b.status === 'fixed');

  if (loading) {
    return (
      <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-5 bg-white/10 rounded w-1/3"></div>
          <div className="h-16 bg-white/10 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-red-400" />
          <h2 className="text-sm font-semibold text-white">Bug Tracker</h2>
          {activeBugs.length > 0 && (
            <span className="px-1.5 py-0.5 bg-red-500/20 rounded text-[10px] text-red-400 font-medium">
              {activeBugs.length} active
            </span>
          )}
        </div>
      </div>

      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {activeBugs.length === 0 ? (
          <div className="text-center py-4 text-white/30">
            <CheckCircle className="w-6 h-6 mx-auto mb-2 text-emerald-400/50" />
            <p className="text-xs">No active bugs</p>
          </div>
        ) : (
          activeBugs.map((bug) => {
            const isExpanded = expandedId === bug.id;
            return (
              <motion.div
                key={bug.id}
                className={`rounded-lg border p-3 cursor-pointer transition-all ${severityColors[bug.severity]}`}
                onClick={() => setExpandedId(isExpanded ? null : bug.id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium uppercase ${severityColors[bug.severity]}`}>
                        {bug.severity}
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-white/50">
                        {statusIcons[bug.status]}
                        {bug.status}
                      </span>
                    </div>
                    <h3 className="text-xs font-medium text-white truncate">{bug.title}</h3>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-white/30 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </div>

                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-3 pt-3 border-t border-white/10 space-y-2"
                  >
                    <div>
                      <div className="text-[10px] text-white/40 uppercase mb-1">Symptoms</div>
                      <p className="text-[11px] text-white/70">{bug.symptoms}</p>
                    </div>
                    
                    {bug.attempts.length > 0 && (
                      <div>
                        <div className="text-[10px] text-white/40 uppercase mb-1">Attempts ({bug.attempts.length})</div>
                        <ul className="space-y-0.5">
                          {bug.attempts.map((a, i) => (
                            <li key={i} className="text-[10px] text-white/50 flex gap-1">
                              <span>•</span><span>{a}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {bug.nextSteps.length > 0 && (
                      <div>
                        <div className="text-[10px] text-white/40 uppercase mb-1">Next Steps</div>
                        <ul className="space-y-0.5">
                          {bug.nextSteps.map((s, i) => (
                            <li key={i} className="text-[10px] text-emerald-400/70 flex gap-1">
                              <span>→</span><span>{s}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="text-[9px] text-white/30 pt-1">
                      Updated: {bug.lastUpdated}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            );
          })
        )}

        {fixedBugs.length > 0 && (
          <div className="pt-2 border-t border-white/5">
            <div className="text-[10px] text-white/30 mb-1">Recently Fixed ({fixedBugs.length})</div>
            {fixedBugs.slice(0, 3).map((bug) => (
              <div key={bug.id} className="text-[10px] text-white/40 flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-emerald-400/50" />
                {bug.title}
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
