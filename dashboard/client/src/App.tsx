/**
 * Mission Control — Premium Dashboard for OpenClaw
 * 
 * A modern, visually-rich dashboard inspired by FiQ, FreshFizi, and production SaaS patterns.
 * 
 * Design principles:
 * - Strong visual hierarchy with big numbers and clear labels
 * - Purple/blue/coral gradient palette for visual interest
 * - Sidebar navigation for easy section switching
 * - Card-based layout with subtle glass morphism
 * - Tasteful motion: entrance animations, hover states, micro-interactions
 * - Dark theme optimized for extended use
 */

import { useState, useEffect, useCallback, Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { api, setAuth, getAuth, clearAuth, createWebSocket } from './lib/api';
import { cn, parseLogLine, formatRelative } from './lib/utils';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Command, RefreshCw, LogOut, Wifi, WifiOff, Search, ChevronDown,
  Edit2, Save, X, FileText, Heart, User, Activity, Brain, Phone,
  Terminal, Sparkles, Settings, LayoutDashboard, Calendar, Bug,
  MessageCircle
} from 'lucide-react';

// Components
import KnowledgeGraph from './components/KnowledgeGraph';
import KnowledgeGraphSearch from './components/KnowledgeGraphSearch';
import MindSynthesis from './components/MindSynthesis';
import MoltbookActivity from './components/MoltbookActivity';
import ExplorationLog from './components/ExplorationLog';
import BugTracker from './components/BugTracker';
import UpcomingTasks from './components/UpcomingTasks';
import Sidebar from './components/Sidebar';
import DashboardView from './components/DashboardView';
import MoodCard from './components/MoodCard';
import { ActionTimeline } from './components/ActionTimeline';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

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
interface ExplorationEntry {
  timestamp: string;
  sessionId: string;
  type: string;
  content: string;
  metadata: Record<string, unknown>;
}

type View = 'dashboard' | 'mind' | 'activity' | 'exploration' | 'memory' | 'calls' | 'tasks' | 'bugs' | 'search' | 'settings';

// ═══════════════════════════════════════════════════════════════════════════
// Error Boundary
// ═══════════════════════════════════════════════════════════════════════════

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
            className="glass-card rounded-2xl p-8 max-w-2xl border-red-500/20"
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

// ═══════════════════════════════════════════════════════════════════════════
// Login Screen
// ═══════════════════════════════════════════════════════════════════════════

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
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/[0.08] rounded-full blur-[128px] float-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/[0.06] rounded-full blur-[128px] float-slow" style={{ animationDelay: '-3s' }} />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-pink-500/[0.04] rounded-full blur-[100px] float-slow" style={{ animationDelay: '-5s' }} />
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
              className="w-14 h-14 mx-auto rounded-2xl gradient-purple-blue flex items-center justify-center"
            >
              <Command className="w-7 h-7 text-white" />
            </motion.div>
            <h1 className="text-xl font-semibold text-white/90">Mission Control</h1>
            <p className="text-sm text-white/40">Sign in to your dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-white/90 placeholder:text-white/25"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl glass-input text-sm text-white/90 placeholder:text-white/25"
            />
            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-red-400/80 text-sm"
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
              className="w-full py-3 rounded-xl gradient-purple-blue text-white font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
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

// ═══════════════════════════════════════════════════════════════════════════
// Header Bar
// ═══════════════════════════════════════════════════════════════════════════

function Header({ online, onRefresh }: { online: boolean; onRefresh: () => void }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="h-16 px-6 flex items-center justify-between border-b border-white/[0.06] bg-[hsl(230,25%,7%)]/80 backdrop-blur-xl"
    >
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl glass-input text-sm text-white/70 placeholder:text-white/30"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Status badge */}
        <div className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium',
          online
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            : 'bg-red-500/10 text-red-400 border border-red-500/20'
        )}>
          {online ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          {online ? 'Online' : 'Offline'}
          {online && <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full pulse-online" />}
        </div>

        <div className="w-px h-6 bg-white/[0.08]" />

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onRefresh}
          className="icon-btn"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => { clearAuth(); window.location.reload(); }}
          className="icon-btn"
          title="Logout"
        >
          <LogOut className="w-4 h-4" />
        </motion.button>
      </div>
    </motion.header>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Collapsible Section (for detail views)
// ═══════════════════════════════════════════════════════════════════════════

function GlassSection({
  title,
  icon: Icon,
  children,
  defaultOpen = false,
  badge,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: ReactNode;
  defaultOpen?: boolean;
  badge?: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <motion.div layout className="glass-card rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-4 h-4 text-white/40" />
          <span className="text-sm font-medium text-white/80">{title}</span>
          {badge}
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="w-4 h-4 text-white/30" />
        </motion.div>
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

// ═══════════════════════════════════════════════════════════════════════════
// Memory View
// ═══════════════════════════════════════════════════════════════════════════

function MemoryView({ mainMemory, memoryFiles }: {
  mainMemory: string | null;
  memoryFiles: MemoryFile[];
}) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const selectedFile = selectedDate ? memoryFiles.find(f => f.date === selectedDate) : null;

  return (
    <div className="p-6 space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-white/90 mb-2">Memory</h1>
        <p className="text-white/50">Long-term memory and daily journals</p>
      </motion.div>

      {/* Timeline pills */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {memoryFiles.slice(0, 14).map((file, i) => (
          <motion.button
            key={file.date}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            onClick={() => setSelectedDate(selectedDate === file.date ? null : file.date)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all shrink-0',
              selectedDate === file.date
                ? 'gradient-purple-blue text-white'
                : 'bg-white/[0.04] text-white/50 hover:text-white/80 border border-white/[0.06]'
            )}
          >
            {new Date(file.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </motion.button>
        ))}
      </div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass-card rounded-2xl p-6"
      >
        <div className="prose prose-invert prose-sm max-w-none max-h-[70vh] overflow-y-auto">
          {selectedFile ? (
            <>
              <h3 className="text-purple-400 text-lg">{selectedFile.date}</h3>
              <ReactMarkdown>{selectedFile.content}</ReactMarkdown>
            </>
          ) : mainMemory ? (
            <ReactMarkdown>{mainMemory}</ReactMarkdown>
          ) : (
            <p className="text-white/30">Loading memory...</p>
          )}
        </div>
      </motion.div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Live Logs
// ═══════════════════════════════════════════════════════════════════════════

function LiveLogs({ logs }: { logs: LogEntry[] }) {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const filters = ['all', 'message', 'tool', 'error', 'heartbeat'];

  const filteredLogs = logs.filter(log => {
    if (filter !== 'all' && log.type !== filter) return false;
    if (search && !log.content.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-white/90 mb-2">Activity Logs</h1>
        <p className="text-white/50">Real-time agent activity</p>
      </motion.div>

      <div className="flex flex-wrap gap-3">
        {/* Filters */}
        <div className="flex gap-2">
          {filters.map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm capitalize transition-all',
                filter === f
                  ? 'gradient-purple-blue text-white'
                  : 'bg-white/[0.04] text-white/40 hover:text-white/70'
              )}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
          <input
            type="text"
            placeholder="Filter logs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg glass-input text-sm text-white/70 placeholder:text-white/20"
          />
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass-card rounded-2xl overflow-hidden"
      >
        <div className="h-[60vh] overflow-y-auto font-mono text-sm terminal-lines bg-black/30 p-4">
          {filteredLogs.length === 0 ? (
            <p className="text-white/20 text-center py-12">No logs to display</p>
          ) : (
            filteredLogs.slice(-300).map((log, i) => (
              <div key={i} className={cn(
                'py-1 border-l-2 pl-3 hover:bg-white/[0.02] transition-colors',
                log.type === 'error' ? 'border-red-400/50 log-error' :
                log.type === 'heartbeat' ? 'border-emerald-400/50 log-heartbeat' :
                log.type === 'tool' ? 'border-purple-400/50 log-tool' :
                log.type === 'message' ? 'border-blue-400/50 log-message' :
                'border-white/10 log-system'
              )}>
                {log.timestamp && (
                  <span className="text-white/20 mr-3 tabular-nums">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                )}
                <span className="break-all">{log.content}</span>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Knowledge Graph View (Full Screen)
// ═══════════════════════════════════════════════════════════════════════════

function KnowledgeGraphView({ state }: { state: AgentState | null }) {
  return (
    <div className="relative h-[calc(100vh-64px)]">
      {/* Status overlay */}
      {state && (
        <div className="absolute top-4 left-4 z-10 bg-black/70 backdrop-blur-xl rounded-xl p-4 border border-white/10">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-purple-400" />
              <Heart className="w-4 h-4 text-white/40" />
              <span className="text-sm text-white/80">{state.mood}</span>
            </div>
            {state.currentActivity && (
              <>
                <div className="w-px h-4 bg-white/20" />
                <span className="text-sm text-emerald-400">{state.currentActivity}</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 bg-black/70 backdrop-blur-xl rounded-xl p-4 border border-white/10 max-w-xs">
        <h3 className="text-sm font-medium text-white/80 mb-3">Node Types</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="text-white/60">Concepts</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-pink-400" />
            <span className="text-white/60">People</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-orange-400" />
            <span className="text-white/60">Projects</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-purple-400" />
            <span className="text-white/60">Questions</span>
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-white/10">
          <KnowledgeGraphSearch />
        </div>
      </div>

      {/* Graph */}
      <KnowledgeGraph />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Main App
// ═══════════════════════════════════════════════════════════════════════════

export default function App() {
  const [authenticated, setAuthenticated] = useState(() => !!getAuth());
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [online, setOnline] = useState(false);
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [files, setFiles] = useState<Record<string, string>>({});
  const [memoryFiles, setMemoryFiles] = useState<MemoryFile[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [calls, setCalls] = useState<Array<{ date: string; target: string; context: string }>>([]);
  const [explorationEntries, setExplorationEntries] = useState<ExplorationEntry[]>([]);

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
      setLogs(logsData.lines.map((line: string) => parseLogLine(line)));

      const callsData = await api.getCalls();
      setCalls(callsData.calls);

      try {
        const stateData = await api.getState();
        setAgentState(stateData);
      } catch {}

      try {
        const explorationData = await api.getExplorationStream(200);
        setExplorationEntries(explorationData.entries);
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

  if (!authenticated) {
    return <Login onLogin={() => setAuthenticated(true)} />;
  }

  // Generate activity data for chart (mock for now, could be derived from actions)
  const activityData = agentState?.recentActions 
    ? [4, 6, 5, 8, 7, 9, agentState.recentActions.length]
    : [3, 5, 4, 7, 6, 8, 9];

  // Render the current view
  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <DashboardView
            state={agentState}
            identity={identity}
            memoryFileCount={memoryFiles.length}
            explorationCount={explorationEntries.length}
            callCount={calls.length}
            activityData={activityData}
          />
        );
      case 'mind':
        return <KnowledgeGraphView state={agentState} />;
      case 'activity':
        return <LiveLogs logs={logs} />;
      case 'exploration':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Exploration</h1>
              <p className="text-white/50">Curiosity sessions and discoveries</p>
            </motion.div>
            <ExplorationLog />
          </div>
        );
      case 'memory':
        return <MemoryView mainMemory={files['MEMORY.md']} memoryFiles={memoryFiles} />;
      case 'tasks':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Tasks</h1>
              <p className="text-white/50">Scheduled and upcoming tasks</p>
            </motion.div>
            <UpcomingTasks />
          </div>
        );
      case 'calls':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Calls</h1>
              <p className="text-white/50">Voice call history</p>
            </motion.div>
            <GlassSection title="Call History" icon={Phone} defaultOpen={true}>
              <div className="space-y-2 mt-3">
                {calls.length === 0 ? (
                  <p className="text-white/30 text-sm text-center py-6">No calls recorded</p>
                ) : (
                  calls.map((call, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02]">
                      <span className="text-sm text-white/70">{call.target}</span>
                      <span className="text-xs text-white/30">{call.date}</span>
                    </div>
                  ))
                )}
              </div>
            </GlassSection>
          </div>
        );
      case 'bugs':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Bug Tracker</h1>
              <p className="text-white/50">Known issues and fixes</p>
            </motion.div>
            <BugTracker />
          </div>
        );
      case 'search':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Search</h1>
              <p className="text-white/50">Search through memory and logs</p>
            </motion.div>
            <KnowledgeGraphSearch />
          </div>
        );
      case 'settings':
        return (
          <div className="p-6 space-y-6">
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-2xl font-bold text-white/90 mb-2">Settings</h1>
              <p className="text-white/50">Configure your dashboard</p>
            </motion.div>
            <div className="grid gap-4">
              <GlassSection title="Soul" icon={Heart} defaultOpen={false}>
                <div className="prose prose-invert prose-sm max-w-none mt-3 max-h-64 overflow-y-auto">
                  <ReactMarkdown>{files['SOUL.md'] || 'Loading...'}</ReactMarkdown>
                </div>
              </GlassSection>
              <GlassSection title="Identity" icon={User} defaultOpen={false}>
                <div className="prose prose-invert prose-sm max-w-none mt-3 max-h-64 overflow-y-auto">
                  <ReactMarkdown>{files['IDENTITY.md'] || 'Loading...'}</ReactMarkdown>
                </div>
              </GlassSection>
              <GlassSection title="User Profile" icon={User} defaultOpen={false}>
                <div className="prose prose-invert prose-sm max-w-none mt-3 max-h-64 overflow-y-auto">
                  <ReactMarkdown>{files['USER.md'] || 'Loading...'}</ReactMarkdown>
                </div>
              </GlassSection>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background mesh-gradient noise">
        {/* Sidebar */}
        <Sidebar
          currentView={currentView}
          onViewChange={setCurrentView}
          identity={identity}
          online={online}
        />

        {/* Main content area */}
        <div className="ml-64">
          <Header online={online} onRefresh={loadData} />
          <main className="min-h-[calc(100vh-64px)] overflow-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentView}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderView()}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}
