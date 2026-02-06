import { useState, useEffect, useCallback, useRef, Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { api, setAuth, getAuth, clearAuth, createWebSocket } from './lib/api';
import { cn, parseLogLine, formatRelative } from './lib/utils';
import ReactMarkdown from 'react-markdown';
import KnowledgeGraph, { KnowledgeGraphExplainer } from './components/KnowledgeGraph';
import MindSynthesis from './components/MindSynthesis';
import MoltbookActivity from './components/MoltbookActivity';
import ExplorationLog from './components/ExplorationLog';
import BugTracker from './components/BugTracker';
import UpcomingTasks from './components/UpcomingTasks';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity, Brain, FileText, Phone, Search, Terminal,
  RefreshCw, Wifi, WifiOff, User, Heart,
  ChevronDown, Edit2, Save, X, LogOut,
  Sparkles, Lightbulb, AlertTriangle, CheckCircle, Clock,
  MessageCircle, Zap, Bug, Command
} from 'lucide-react';

// ─── Animation Variants ───

const fadeIn = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
};

const stagger = {
  animate: { transition: { staggerChildren: 0.04 } },
};

const cardSpring = {
  type: 'spring' as const,
  stiffness: 400,
  damping: 30,
};

// ─── Error Boundary ───

interface ErrorBoundaryProps { children: ReactNode; }
interface ErrorBoundaryState { hasError: boolean; error: Error | null; errorInfo: ErrorInfo | null; }

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 noise">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass rounded-2xl p-8 max-w-2xl border-red-500/20"
          >
            <h1 className="text-2xl font-semibold text-red-400 mb-4">Dashboard Error</h1>
            <p className="text-red-300/80 mb-4 text-sm">Something went wrong loading the dashboard.</p>
            <div className="bg-black/40 rounded-xl p-4 font-mono text-sm text-red-200/80 overflow-auto max-h-64">
              <p className="font-medium">{this.state.error?.toString()}</p>
              <pre className="mt-2 text-xs opacity-60">{this.state.errorInfo?.componentStack}</pre>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="mt-5 px-5 py-2.5 bg-red-500/20 text-red-300 rounded-xl hover:bg-red-500/30 transition-colors text-sm font-medium border border-red-500/20"
            >
              Reload Dashboard
            </button>
          </motion.div>
        </div>
      );
    }
    return this.props.children;
  }
}

// ─── Types ───

interface LogEntry { type: string; content: string; timestamp?: string; }
interface MemoryFile { name: string; date: string; modified: string; preview: string; content: string; }
interface Identity { name: string; vibe: string; emoji: string; }
interface AgentState {
  lastUpdated: string | null;
  mood: string;
  topOfMind: string[];
  recentLearnings: string[];
  currentActivity: string | null;
  recentActions: Array<{ action: string; target?: string; timestamp: string; outcome: string; notes?: string }>;
  questionsOnMyMind: string[];
}
interface DebugAction {
  type: string;
  startTime: string;
  steps: Array<{ time: string; event: string; detail: string }>;
  status: string;
}
interface ExplorationEntry {
  timestamp: string;
  sessionId: string;
  type: string;
  content: string;
  metadata: Record<string, unknown>;
}

// ─── Reusable Glass Section ───

function GlassSection({
  title,
  icon: Icon,
  children,
  defaultOpen = false,
  badge,
  headerRight,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: ReactNode;
  defaultOpen?: boolean;
  badge?: ReactNode;
  headerRight?: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <motion.div
      layout
      transition={cardSpring}
      className="glass rounded-2xl overflow-hidden"
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-4 h-4 text-white/40" />
          <span className="text-sm font-medium text-white/80">{title}</span>
          {badge}
        </div>
        <div className="flex items-center gap-2">
          {headerRight}
          <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-4 h-4 text-white/30" />
          </motion.div>
        </div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-white/[0.04]">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ─── Login ───

function Login({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setAuth(username, password);
    try {
      await api.getGatewayStatus();
      onLogin();
    } catch {
      setError('Invalid credentials');
      clearAuth();
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background mesh-gradient noise">
      {/* Ambient orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/[0.04] rounded-full blur-[128px] float-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/[0.03] rounded-full blur-[128px] float-slow" style={{ animationDelay: '-3s' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="relative w-full max-w-sm"
      >
        <div className="glass-strong rounded-2xl p-8 space-y-6">
          <div className="text-center space-y-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 300 }}
              className="w-12 h-12 mx-auto rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center"
            >
              <Command className="w-6 h-6 text-emerald-400" />
            </motion.div>
            <h1 className="text-lg font-semibold text-white/90">Mission Control</h1>
            <p className="text-xs text-white/40">OpenClaw Dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl glass-input text-sm text-white/90 placeholder:text-white/25"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl glass-input text-sm text-white/90 placeholder:text-white/25"
            />
            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-red-400/80 text-xs"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-emerald-500/20 text-emerald-300 font-medium text-sm hover:bg-emerald-500/30 transition-colors disabled:opacity-40 border border-emerald-500/20"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Connecting...
                </span>
              ) : 'Sign in'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Command Bar (Status Header) ───

function CommandBar({
  identity,
  online,
  onRefresh,
}: {
  identity: Identity | null;
  online: boolean;
  onRefresh: () => void;
}) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="sticky top-0 z-50 glass-strong border-b border-white/[0.04]"
    >
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Left: identity */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-sm">
            {identity?.emoji || <Command className="w-3.5 h-3.5 text-emerald-400" />}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-white/80">
              {identity?.name === '(discovering)' ? 'Mission Control' : identity?.name || 'Mission Control'}
            </span>
            <span className="text-white/20">/</span>
            <span className="text-xs text-white/40 hidden sm:inline truncate max-w-[200px]">
              {identity?.vibe || 'Dashboard'}
            </span>
          </div>
        </div>

        {/* Right: status + actions */}
        <div className="flex items-center gap-2">
          {/* Online status */}
          <div className={cn(
            'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors',
            online
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-red-500/10 text-red-400 border border-red-500/20'
          )}>
            {online ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            <span className="hidden sm:inline">{online ? 'Online' : 'Offline'}</span>
            {online && <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full pulse-online" />}
          </div>

          <div className="w-px h-5 bg-white/[0.06] mx-1" />

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onRefresh}
            className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-3.5 h-3.5 text-white/40" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => { clearAuth(); window.location.reload(); }}
            className="p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5 text-white/40" />
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
}

// ─── Hero Section (Agent State) ───

function HeroSection({ state }: { state: AgentState | null }) {
  const moodEmoji = !state ? null
    : state.mood.includes('curious') ? '?'
    : state.mood.includes('happy') || state.mood.includes('good') ? ':)'
    : state.mood.includes('tired') ? 'zzz'
    : state.mood.includes('focused') ? '>'
    : state.mood.includes('excited') ? '!'
    : '.';

  if (!state) {
    return (
      <motion.div {...fadeIn} className="glass rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-2 h-2 rounded-full bg-white/30 shimmer" />
          <span className="text-sm text-white/40">Loading state...</span>
        </div>
        <div className="h-16 shimmer rounded-xl" />
      </motion.div>
    );
  }

  return (
    <motion.div
      {...fadeIn}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-2xl"
    >
      {/* Ambient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.06] via-transparent to-blue-500/[0.04]" />
      <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/[0.04] rounded-full blur-[80px]" />

      <div className="relative glass rounded-2xl p-6 sm:p-8">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-purple-400" />
            <span className="text-xs font-medium text-white/30 uppercase tracking-wider">Status</span>
          </div>
          {state.lastUpdated && (
            <span className="text-xs text-white/25">
              {formatRelative(state.lastUpdated)}
            </span>
          )}
        </div>

        {/* Main hero content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Mood */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-white/30">
              <Heart className="w-3 h-3" />
              Mood
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-mono text-purple-300/60">{moodEmoji}</span>
              <span className="text-lg font-medium text-white/80">{state.mood}</span>
            </div>
          </div>

          {/* Current activity */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-white/30">
              <Zap className="w-3 h-3" />
              Activity
            </div>
            <div className="flex items-center gap-3">
              {state.currentActivity ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-online" />
                  <span className="text-lg font-medium text-white/80">{state.currentActivity}</span>
                </>
              ) : (
                <span className="text-lg text-white/30">Idle</span>
              )}
            </div>
          </div>
        </div>

        {/* Cards row */}
        <motion.div variants={stagger} initial="initial" animate="animate" className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Top of mind */}
          {state.topOfMind.length > 0 && (
            <motion.div variants={fadeIn} className="bg-white/[0.02] rounded-xl p-4 border border-white/[0.04]">
              <div className="flex items-center gap-2 text-xs text-white/30 mb-3">
                <Brain className="w-3 h-3" />
                On my mind
              </div>
              <div className="space-y-1.5">
                {state.topOfMind.slice(0, 3).map((item, i) => (
                  <p key={i} className="text-xs text-white/60 leading-relaxed">{item}</p>
                ))}
              </div>
            </motion.div>
          )}

          {/* Recent learnings */}
          {state.recentLearnings.length > 0 && (
            <motion.div variants={fadeIn} className="bg-white/[0.02] rounded-xl p-4 border border-white/[0.04]">
              <div className="flex items-center gap-2 text-xs text-white/30 mb-3">
                <Lightbulb className="w-3 h-3" />
                Learnings
              </div>
              <div className="space-y-1.5">
                {state.recentLearnings.slice(0, 3).map((item, i) => (
                  <p key={i} className="text-xs text-amber-300/60 leading-relaxed">{item}</p>
                ))}
              </div>
            </motion.div>
          )}

          {/* Questions */}
          {state.questionsOnMyMind.length > 0 && (
            <motion.div variants={fadeIn} className="bg-white/[0.02] rounded-xl p-4 border border-white/[0.04]">
              <div className="flex items-center gap-2 text-xs text-white/30 mb-3">
                <MessageCircle className="w-3 h-3" />
                Pondering
              </div>
              <div className="space-y-1.5">
                {state.questionsOnMyMind.slice(0, 3).map((item, i) => (
                  <p key={i} className="text-xs text-cyan-300/60 italic leading-relaxed">{item}</p>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

// ─── Action Timeline ───

function ActionTimeline({ actions }: { actions: AgentState['recentActions'] }) {
  if (!actions || actions.length === 0) return null;

  return (
    <motion.div {...fadeIn} className="glass rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-white/30" />
        <span className="text-sm font-medium text-white/60">Recent Actions</span>
        <span className="text-xs text-white/20 ml-auto">{actions.length} total</span>
      </div>

      <div className="relative timeline-line">
        <motion.div variants={stagger} initial="initial" animate="animate" className="space-y-1">
          {actions.slice(0, 8).map((action, i) => (
            <motion.div
              key={`${action.timestamp}-${i}`}
              variants={fadeIn}
              className="flex items-center gap-3 py-2 pl-8 group"
            >
              {/* Dot */}
              <div className={cn(
                'absolute left-[11px] w-[9px] h-[9px] rounded-full border-2 bg-background z-10',
                action.outcome === 'success' ? 'border-emerald-400' :
                action.outcome === 'error' ? 'border-red-400' :
                'border-yellow-400'
              )} />

              {/* Content */}
              <div className="flex-1 flex items-center justify-between min-w-0">
                <div className="flex items-center gap-2 min-w-0">
                  {action.outcome === 'success' ? (
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400/60 shrink-0" />
                  ) : action.outcome === 'error' ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400/60 shrink-0" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-yellow-400/60 shrink-0" />
                  )}
                  <span className="text-xs text-white/70 truncate">
                    {(action.action || '').replace(/_/g, ' ')}
                  </span>
                  {action.target && (
                    <span className="text-xs text-white/25 truncate hidden sm:inline">
                      {action.target}
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-white/20 shrink-0 ml-2 tabular-nums">
                  {new Date(action.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
}

// ─── Live Exploration Stream ───

function ExplorationStream({ entries, isActive }: { entries: ExplorationEntry[]; isActive: boolean }) {
  const streamEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (streamEndRef.current) {
      streamEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [entries]);

  const getTypeColor = (type: string) => {
    // Subtle, monochrome styling - no color carnival
    switch (type) {
      case 'start':
      case 'end': return 'border-l-white/20';
      case 'discovery': return 'border-l-emerald-500/40';
      default: return 'border-l-white/10';
    }
  };

  const getTypeLabel = (type: string) => {
    // Simple, lowercase labels
    const labels: Record<string, string> = {
      thought: 'thinking',
      tool_call: 'action',
      tool_result: 'result',
      discovery: 'insight',
      question: 'question',
      reflection: 'reflection',
      start: 'started',
      end: 'finished',
    };
    return labels[type] || type;
  };

  // Group entries by session
  const sessions = entries.reduce((acc, entry) => {
    if (!acc[entry.sessionId]) acc[entry.sessionId] = [];
    acc[entry.sessionId].push(entry);
    return acc;
  }, {} as Record<string, ExplorationEntry[]>);

  return (
    <GlassSection
      title="Exploration"
      icon={Sparkles}
      defaultOpen={false}
      badge={isActive ? (
        <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400">
          <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
          Active
        </span>
      ) : undefined}
      headerRight={
        <span className="text-[10px] text-white/20 tabular-nums">{entries.length}</span>
      }
    >
      <div className="mt-3 max-h-[420px] overflow-y-auto">
        {entries.length === 0 ? (
          <div className="text-center py-12">
            <Sparkles className="w-8 h-8 mx-auto mb-3 text-white/10" />
            <p className="text-sm text-white/25">No exploration in progress</p>
            <p className="text-xs text-white/15 mt-1">Stream of consciousness appears here in real-time</p>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(sessions).map(([sessionId, sessionEntries]) => (
              <div key={sessionId} className="space-y-1.5">
                <div className="flex items-center gap-3 text-[10px] text-white/20 uppercase tracking-widest py-1">
                  <span className="w-6 h-px bg-white/[0.06]" />
                  {sessionId}
                  <span className="flex-1 h-px bg-white/[0.06]" />
                </div>
                {sessionEntries.map((entry, i) => (
                  <motion.div
                    key={`${entry.timestamp}-${i}`}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={cn('p-3 rounded-lg border-l-2', getTypeColor(entry.type))}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] text-white/30">
                        {getTypeLabel(entry.type)}
                      </span>
                      <span className="text-[10px] text-white/15 tabular-nums">
                        {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-xs text-white/60 whitespace-pre-wrap break-words leading-relaxed">
                      {entry.content}
                    </p>
                    {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                      <div className="mt-1.5 flex gap-3 text-[10px] text-white/20">
                        {entry.metadata.tool ? <span>tool: {String(entry.metadata.tool)}</span> : null}
                        {entry.metadata.source ? <span>src: {String(entry.metadata.source)}</span> : null}
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            ))}
            <div ref={streamEndRef} />
          </div>
        )}
      </div>
    </GlassSection>
  );
}

// ─── Live Logs ───

function LiveLogs({ logs, filter, setFilter }: {
  logs: LogEntry[];
  filter: string;
  setFilter: (f: string) => void;
}) {
  const [search, setSearch] = useState('');
  const [paused, setPaused] = useState(false);
  const filters = ['all', 'message', 'tool', 'error', 'heartbeat'];

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.type !== filter) return false;
    if (search && !log.content.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <GlassSection
      title="Activity Log"
      icon={Terminal}
      defaultOpen={false}
      headerRight={
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={(e) => { e.stopPropagation(); setPaused(!paused); }}
          className={cn(
            'px-2 py-0.5 rounded-md text-[10px] font-medium transition-colors',
            paused ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20' : 'bg-white/[0.04] text-white/30'
          )}
        >
          {paused ? 'Paused' : 'Pause'}
        </motion.button>
      }
    >
      <div className="mt-3 space-y-3">
        {/* Filters */}
        <div className="flex gap-1.5 flex-wrap">
          {filters.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'px-2.5 py-1 rounded-lg text-[11px] capitalize transition-all',
                filter === f
                  ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                  : 'bg-white/[0.03] text-white/30 hover:text-white/50 border border-transparent'
              )}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/20" />
          <input
            type="text"
            placeholder="Filter logs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg glass-input text-xs text-white/70 placeholder:text-white/20"
          />
        </div>

        {/* Log entries */}
        <div className="h-72 overflow-y-auto font-mono text-xs space-y-px terminal-lines rounded-lg bg-black/20 p-3">
          {filteredLogs.length === 0 ? (
            <p className="text-white/20 text-center py-8">No logs to display</p>
          ) : (
            filteredLogs.slice(-200).map((log, i) => (
              <div key={i} className={cn(
                'py-0.5 border-l-2 pl-2.5 hover:bg-white/[0.02] transition-colors',
                log.type === 'error' ? 'border-red-400/50 log-error' :
                log.type === 'heartbeat' ? 'border-emerald-400/50 log-heartbeat' :
                log.type === 'tool' ? 'border-amber-400/50 log-tool' :
                log.type === 'message' ? 'border-blue-400/50 log-message' :
                'border-white/10 log-system'
              )}>
                {log.timestamp && (
                  <span className="text-white/15 mr-2 tabular-nums">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                )}
                <span className="break-all">{log.content}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </GlassSection>
  );
}

// ─── Memory View ───

function MemoryView({ mainMemory, memoryFiles }: {
  mainMemory: string | null;
  memoryFiles: MemoryFile[];
}) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const selectedFile = selectedDate ? memoryFiles.find(f => f.date === selectedDate) : null;

  return (
    <GlassSection title="Memory & World Model" icon={Brain} defaultOpen={false}>
      <div className="mt-3 space-y-4">
        {/* Timeline pills */}
        <div className="flex gap-1.5 overflow-x-auto pb-1">
          {memoryFiles.slice(0, 14).map(file => (
            <button
              key={file.date}
              onClick={() => setSelectedDate(selectedDate === file.date ? null : file.date)}
              className={cn(
                'px-2.5 py-1 rounded-lg text-[11px] whitespace-nowrap transition-all shrink-0',
                selectedDate === file.date
                  ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                  : 'bg-white/[0.03] text-white/30 hover:text-white/50 border border-transparent'
              )}
            >
              {new Date(file.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="prose prose-invert prose-sm max-w-none max-h-80 overflow-y-auto text-xs leading-relaxed">
          {selectedFile ? (
            <>
              <h3 className="text-emerald-400/80 text-sm">{selectedFile.date}</h3>
              <ReactMarkdown>{selectedFile.content}</ReactMarkdown>
            </>
          ) : mainMemory ? (
            <ReactMarkdown>{mainMemory}</ReactMarkdown>
          ) : (
            <p className="text-white/20">Loading memory...</p>
          )}
        </div>
      </div>
    </GlassSection>
  );
}

// ─── File Editor ───

function FileEditor({
  title,
  icon: Icon,
  content,
  onSave,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  content: string | null;
  onSave: (content: string) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleEdit = () => {
    setEditContent(content || '');
    setEditing(true);
    setExpanded(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(editContent);
      setEditing(false);
    } catch (err) {
      console.error('Failed to save:', err);
    }
    setSaving(false);
  };

  return (
    <motion.div layout transition={cardSpring} className="glass rounded-2xl overflow-hidden">
      <button
        onClick={() => !editing && setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-4 h-4 text-white/40" />
          <span className="text-sm font-medium text-white/80">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {!editing && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => { e.stopPropagation(); handleEdit(); }}
              className="p-1.5 rounded-md hover:bg-white/[0.06] transition-colors"
            >
              <Edit2 className="w-3 h-3 text-white/30" />
            </motion.button>
          )}
          {!editing && (
            <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
              <ChevronDown className="w-4 h-4 text-white/30" />
            </motion.div>
          )}
        </div>
      </button>

      <AnimatePresence initial={false}>
        {(expanded || editing) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-white/[0.04]">
              {editing ? (
                <div className="mt-3 space-y-3">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full h-80 p-3 rounded-xl glass-input font-mono text-xs text-white/70 resize-none leading-relaxed"
                  />
                  <div className="flex gap-2 justify-end">
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setEditing(false)}
                      className="px-3 py-1.5 rounded-lg bg-white/[0.04] text-white/40 text-xs hover:bg-white/[0.06] transition-colors flex items-center gap-1.5"
                    >
                      <X className="w-3 h-3" />
                      Cancel
                    </motion.button>
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSave}
                      disabled={saving}
                      className="px-3 py-1.5 rounded-lg bg-emerald-500/15 text-emerald-300 text-xs hover:bg-emerald-500/25 transition-colors disabled:opacity-40 flex items-center gap-1.5 border border-emerald-500/20"
                    >
                      <Save className="w-3 h-3" />
                      {saving ? 'Saving...' : 'Save'}
                    </motion.button>
                  </div>
                </div>
              ) : (
                <div className="mt-3 prose prose-invert prose-sm max-w-none max-h-64 overflow-y-auto text-xs">
                  {content ? (
                    <ReactMarkdown>{content}</ReactMarkdown>
                  ) : (
                    <p className="text-white/20">Loading...</p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ─── Call History ───

function CallHistory({ calls }: { calls: Array<{ date: string; target: string; context: string }> }) {
  return (
    <GlassSection title="Call History" icon={Phone} defaultOpen={false}>
      <div className="mt-3 max-h-64 overflow-y-auto">
        {calls.length === 0 ? (
          <p className="text-white/20 text-xs text-center py-6">No calls recorded</p>
        ) : (
          <div className="space-y-2">
            {calls.map((call, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.03 }}
                className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-white/70">{call.target}</span>
                  <span className="text-[10px] text-white/20 tabular-nums">{call.date}</span>
                </div>
                <p className="text-[11px] text-white/35 mt-1 leading-relaxed">{call.context}</p>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </GlassSection>
  );
}

// ─── Search Panel ───

function SearchPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Array<{ file: string; matches: Array<{ line: string; num: number }> }>>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const data = await api.search(query);
      setResults(data.results);
    } catch (err) {
      console.error('Search failed:', err);
    }
    setSearching(false);
  };

  return (
    <GlassSection title="Search" icon={Search} defaultOpen={false}>
      <div className="mt-3 space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/20" />
            <input
              type="text"
              placeholder="Search across all files..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-9 pr-3 py-2 rounded-lg glass-input text-xs text-white/70 placeholder:text-white/20"
            />
          </div>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSearch}
            disabled={searching}
            className="px-3 py-2 rounded-lg bg-emerald-500/15 text-emerald-300 text-xs hover:bg-emerald-500/25 transition-colors disabled:opacity-40 border border-emerald-500/20"
          >
            {searching ? '...' : 'Go'}
          </motion.button>
        </div>

        {results.length > 0 && (
          <div className="max-h-64 overflow-y-auto space-y-3">
            {results.map((result, i) => (
              <div key={i}>
                <h3 className="text-xs font-medium text-emerald-400/70 mb-1.5 font-mono">{result.file}</h3>
                {result.matches.map((match, j) => (
                  <div key={j} className="text-[11px] py-0.5 border-l border-emerald-500/20 pl-2.5 text-white/50 mb-0.5">
                    <span className="text-white/20 mr-1.5 tabular-nums">L{match.num}</span>
                    {match.line}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </GlassSection>
  );
}

// ─── Debug Console ───

function DebugConsole({ actions }: { actions: DebugAction[] }) {
  const [selectedAction, setSelectedAction] = useState<DebugAction | null>(null);

  return (
    <GlassSection
      title="Debug Console"
      icon={Bug}
      defaultOpen={false}
      badge={
        <span className="text-[9px] font-medium uppercase tracking-wider text-amber-400/50 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/10">
          Infra
        </span>
      }
    >
      <div className="mt-3">
        {actions.length === 0 ? (
          <p className="text-white/20 text-xs text-center py-8">
            No recent actions to debug
          </p>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {/* Action List */}
            <div className="space-y-1.5 max-h-72 overflow-y-auto">
              {actions.map((action, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedAction(selectedAction === action ? null : action)}
                  className={cn(
                    'w-full text-left p-3 rounded-xl transition-all text-xs',
                    selectedAction === action
                      ? 'bg-emerald-500/10 border border-emerald-500/20'
                      : 'bg-white/[0.02] border border-white/[0.04] hover:bg-white/[0.04]'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {action.status === 'success' ? (
                        <CheckCircle className="w-3 h-3 text-emerald-400/60" />
                      ) : action.status === 'error' ? (
                        <AlertTriangle className="w-3 h-3 text-red-400/60" />
                      ) : (
                        <Clock className="w-3 h-3 text-amber-400/60 animate-pulse" />
                      )}
                      <span className="font-medium text-white/60 capitalize">{(action.type || '').replace(/_/g, ' ')}</span>
                    </div>
                    <span className="text-[10px] text-white/20 tabular-nums">
                      {new Date(action.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div className="text-[10px] text-white/25 mt-1">
                    {action.steps.length} steps
                  </div>
                </button>
              ))}
            </div>

            {/* Step Detail */}
            <div className="bg-black/20 rounded-xl p-3 max-h-72 overflow-y-auto">
              {selectedAction ? (
                <div className="space-y-1.5 font-mono text-[11px]">
                  {selectedAction.steps.map((step, i) => (
                    <div
                      key={i}
                      className={cn(
                        'p-2 rounded-lg border-l-2',
                        step.event === 'error' ? 'border-red-400/50 bg-red-500/[0.04]' :
                        step.event === 'completed' ? 'border-emerald-400/50 bg-emerald-500/[0.04]' :
                        step.event === 'initiated' ? 'border-blue-400/50 bg-blue-500/[0.04]' :
                        'border-white/10 bg-white/[0.02]'
                      )}
                    >
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className={cn(
                          'px-1 py-px rounded text-[9px] uppercase font-bold',
                          step.event === 'error' ? 'bg-red-500/20 text-red-300/70' :
                          step.event === 'completed' ? 'bg-emerald-500/20 text-emerald-300/70' :
                          step.event === 'initiated' ? 'bg-blue-500/20 text-blue-300/70' :
                          'bg-white/10 text-white/40'
                        )}>
                          {step.event}
                        </span>
                        <span className="text-white/20 tabular-nums">
                          {new Date(step.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                      </div>
                      <div className="text-white/40 break-all leading-relaxed">
                        {step.detail.length > 150 ? step.detail.slice(0, 150) + '...' : step.detail}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Bug className="w-6 h-6 mx-auto mb-2 text-white/10" />
                  <p className="text-[11px] text-white/20">Select an action to trace</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </GlassSection>
  );
}

// ─── Main App ───

export default function App() {
  const [authenticated, setAuthenticated] = useState(!!getAuth());
  const [online, setOnline] = useState(false);
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [logFilter, setLogFilter] = useState('all');
  const [files, setFiles] = useState<Record<string, string>>({});
  const [memoryFiles, setMemoryFiles] = useState<MemoryFile[]>([]);
  const [calls, setCalls] = useState<Array<{ date: string; target: string; context: string }>>([]);
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [debugActions, setDebugActions] = useState<DebugAction[]>([]);
  const [explorationEntries, setExplorationEntries] = useState<ExplorationEntry[]>([]);
  const [explorationActive, setExplorationActive] = useState(false);
  const [showFilesPanel, setShowFilesPanel] = useState(false);

  const parseIdentity = (content: string): Identity => {
    const lines = content.split('\n');
    const identity: Identity = { name: '', vibe: '', emoji: '' };
    for (const line of lines) {
      if (line.startsWith('name:')) identity.name = line.replace('name:', '').trim();
      if (line.startsWith('vibe:')) identity.vibe = line.replace('vibe:', '').trim();
      if (line.startsWith('emoji:')) identity.emoji = line.replace('emoji:', '').trim();
    }
    return identity;
  };

  const loadData = useCallback(async () => {
    try {
      const status = await api.getGatewayStatus();
      setOnline(status.online);

      const fileNames = ['SOUL.md', 'USER.md', 'AGENTS.md', 'IDENTITY.md', 'MEMORY.md', 'HEARTBEAT.md'];
      const fileContents: Record<string, string> = {};
      for (const name of fileNames) {
        try {
          const data = await api.getFile(name);
          fileContents[name] = data.content;
        } catch {}
      }
      setFiles(fileContents);

      if (fileContents['IDENTITY.md']) {
        setIdentity(parseIdentity(fileContents['IDENTITY.md']));
      }

      const memory = await api.getMemoryFiles();
      setMemoryFiles(memory.files);

      const logsData = await api.getLogs();
      setLogs(logsData.lines.map(line => parseLogLine(line)));

      const callsData = await api.getCalls();
      setCalls(callsData.calls);

      try {
        const stateData = await api.getState();
        setAgentState(stateData);
      } catch {}

      try {
        const debugData = await api.getDebugActions();
        setDebugActions(debugData.actions);
      } catch {}

      try {
        const explorationData = await api.getExplorationStream(200);
        setExplorationEntries(explorationData.entries);
        setExplorationActive(explorationData.activeSession);
      } catch {}
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  }, []);

  useEffect(() => {
    if (!authenticated) return;

    loadData();

    let ws: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      ws = createWebSocket();

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'log') {
            setLogs(prev => [...prev.slice(-999), parseLogLine(msg.line)]);
          } else if (msg.type === 'file_change') {
            loadData();
          } else if (msg.type === 'state_update') {
            setAgentState(msg.state);
          } else if (msg.type === 'exploration_update') {
            setExplorationEntries(prev => [...prev.slice(-199), msg.entry]);
            setExplorationActive(true);
          }
        } catch {}
      };

      ws.onclose = () => {
        reconnectTimeout = setTimeout(connect, 5000);
      };

      ws.onerror = () => {
        ws?.close();
      };
    };

    connect();

    const interval = setInterval(loadData, 30000);

    return () => {
      ws?.close();
      clearTimeout(reconnectTimeout);
      clearInterval(interval);
    };
  }, [authenticated, loadData]);

  const handleSaveFile = async (filename: string, content: string) => {
    await api.saveFile(filename, content);
    setFiles(prev => ({ ...prev, [filename]: content }));
    if (filename === 'IDENTITY.md') {
      setIdentity(parseIdentity(content));
    }
  };

  if (!authenticated) {
    return <Login onLogin={() => setAuthenticated(true)} />;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background mesh-gradient noise">
        {/* Command Bar */}
        <CommandBar identity={identity} online={online} onRefresh={loadData} />

        {/* Top Section */}
        <div className="px-8 py-6">
          <motion.div initial="initial" animate="animate" variants={stagger}>
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2">
                <HeroSection state={agentState} />
              </div>
              <div>
                <ActionTimeline actions={agentState?.recentActions || []} />
              </div>
            </div>
          </motion.div>
        </div>
        
        {/* Knowledge Graph - Full Viewport Width, Like Google Maps */}
        <div className="relative">
          <KnowledgeGraph />
          
          {/* Explanation - Overlaid, blends into background */}
          <div className="absolute top-6 left-8 z-10 max-w-xs pointer-events-none">
            <KnowledgeGraphExplainer />
          </div>
        </div>
        
        {/* Bottom Section */}
        <div className="px-8 py-6">
          <motion.div initial="initial" animate="animate" variants={stagger}>
            {/* Three Column Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Mind Synthesis */}
              <MindSynthesis
                soul={files['SOUL.md'] || ''}
                identity={files['IDENTITY.md'] || ''}
                user={files['USER.md'] || ''}
                memory={files['MEMORY.md'] || ''}
                onOpenFiles={() => setShowFilesPanel(true)}
              />
              
              {/* Exploration + Activity */}
              <div className="space-y-4">
                <ExplorationLog />
                <ExplorationStream entries={explorationEntries} isActive={explorationActive} />
                <LiveLogs logs={logs} filter={logFilter} setFilter={setLogFilter} />
              </div>
              
              {/* Operations */}
              <div className="space-y-4">
                <UpcomingTasks />
                <BugTracker />
                <MemoryView mainMemory={files['MEMORY.md']} memoryFiles={memoryFiles} />
                <CallHistory calls={calls} />
                <MoltbookActivity />
                <SearchPanel />
                <DebugConsole actions={debugActions} />
              </div>
            </div>

            {/* Files Panel (hidden by default) */}
            <AnimatePresence>
              {showFilesPanel && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass rounded-2xl overflow-hidden"
                >
                  <div className="p-4 flex items-center justify-between border-b border-white/5">
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4 text-white/40" />
                      <span className="text-sm font-medium text-white/80">Configuration Files</span>
                    </div>
                    <button
                      onClick={() => setShowFilesPanel(false)}
                      className="text-xs text-white/30 hover:text-white/50"
                    >
                      Close
                    </button>
                  </div>
                  <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <FileEditor title="Soul" icon={Heart} content={files['SOUL.md']} onSave={(c) => handleSaveFile('SOUL.md', c)} />
                    <FileEditor title="Identity" icon={User} content={files['IDENTITY.md']} onSave={(c) => handleSaveFile('IDENTITY.md', c)} />
                    <FileEditor title="User Profile" icon={User} content={files['USER.md']} onSave={(c) => handleSaveFile('USER.md', c)} />
                    <FileEditor title="Heartbeat" icon={Activity} content={files['HEARTBEAT.md']} onSave={(c) => handleSaveFile('HEARTBEAT.md', c)} />
                    <FileEditor title="Agent Instructions" icon={FileText} content={files['AGENTS.md']} onSave={(c) => handleSaveFile('AGENTS.md', c)} />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
