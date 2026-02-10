/**
 * DashboardView — Premium Agent Dashboard
 * 
 * Design: Linear/Vercel inspired
 * - Clean, information-dense
 * - Muted teal accent
 * - No AI-aesthetic (no purple gradients, no glassmorphism)
 * - Subtle, purposeful animations
 */

import { motion } from 'framer-motion';
import { 
  Activity, Brain, Lightbulb, Phone, 
  Clock, CheckCircle, AlertCircle, ArrowUpRight, ArrowDownRight,
  Zap
} from 'lucide-react';

interface AgentState {
  mood: string;
  currentActivity: string | null;
  topOfMind: string[];
  recentLearnings: string[];
  questionsOnMyMind: string[];
  lastUpdated: string | null;
  recentActions: Array<{
    action: string;
    target?: string;
    timestamp: string;
    outcome: string;
    notes?: string;
  }>;
}

interface DashboardViewProps {
  state: AgentState | null;
  identity: { name: string; emoji: string } | null;
  memoryFileCount: number;
  explorationCount: number;
  callCount: number;
  activityData: number[];
}

// Animation variants
const stagger = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
};

const fadeUp = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.25 } }
};

// Stat Card Component
function StatCard({ 
  label, 
  value, 
  change,
  icon: Icon 
}: { 
  label: string; 
  value: number | string; 
  change?: { value: number; positive: boolean };
  icon: typeof Activity;
}) {
  return (
    <motion.div 
      variants={fadeUp}
      className="p-5 rounded-lg"
      style={{ 
        backgroundColor: 'var(--gray-2)', 
        border: '1px solid var(--gray-4)' 
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div 
          className="p-2 rounded-md"
          style={{ backgroundColor: 'var(--gray-4)' }}
        >
          <Icon size={16} style={{ color: 'var(--gray-10)' }} />
        </div>
        {change && (
          <span 
            className="flex items-center gap-1 text-xs font-medium px-2 py-1 rounded"
            style={{ 
              backgroundColor: change.positive ? 'rgba(48, 164, 108, 0.1)' : 'rgba(229, 72, 77, 0.1)',
              color: change.positive ? 'var(--success)' : 'var(--error)'
            }}
          >
            {change.positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {Math.abs(change.value)}%
          </span>
        )}
      </div>
      <div 
        className="text-3xl font-semibold mb-1"
        style={{ 
          color: 'var(--gray-14)',
          fontVariantNumeric: 'tabular-nums',
          letterSpacing: '-0.02em'
        }}
      >
        {value}
      </div>
      <div className="text-sm" style={{ color: 'var(--gray-10)' }}>
        {label}
      </div>
    </motion.div>
  );
}

// Activity Item Component
function ActivityItem({ 
  action, 
  timestamp, 
  outcome 
}: { 
  action: string; 
  timestamp: string; 
  outcome: string;
}) {
  const isSuccess = outcome === 'success';
  return (
    <div 
      className="flex items-center gap-3 py-3 border-b"
      style={{ borderColor: 'var(--gray-4)' }}
    >
      <div 
        className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ 
          backgroundColor: isSuccess ? 'rgba(48, 164, 108, 0.15)' : 'rgba(245, 166, 35, 0.15)'
        }}
      >
        {isSuccess 
          ? <CheckCircle size={12} style={{ color: 'var(--success)' }} />
          : <AlertCircle size={12} style={{ color: 'var(--warning)' }} />
        }
      </div>
      <div className="flex-1 min-w-0">
        <div 
          className="text-sm truncate"
          style={{ color: 'var(--gray-13)' }}
        >
          {action.replace(/_/g, ' ')}
        </div>
      </div>
      <div 
        className="text-xs font-mono"
        style={{ color: 'var(--gray-9)' }}
      >
        {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}

// Mind Section Component
function MindSection({ 
  title, 
  items, 
  icon: Icon,
  accentColor 
}: { 
  title: string; 
  items: string[];
  icon: typeof Brain;
  accentColor: string;
}) {
  if (!items || items.length === 0) return null;
  
  return (
    <div className="mb-6 last:mb-0">
      <div className="flex items-center gap-2 mb-3">
        <Icon size={14} style={{ color: accentColor }} />
        <span 
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: 'var(--gray-9)' }}
        >
          {title}
        </span>
      </div>
      <ul className="space-y-2">
        {items.slice(0, 3).map((item, i) => (
          <li 
            key={i}
            className="text-sm leading-relaxed"
            style={{ color: 'var(--gray-12)' }}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function DashboardView({
  state,
  identity,
  memoryFileCount,
  explorationCount,
  callCount,
}: DashboardViewProps) {
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  
  const actionsToday = state?.recentActions?.filter(a => {
    return new Date(a.timestamp).toDateString() === new Date().toDateString();
  }).length || 0;

  const successRate = state?.recentActions?.length
    ? Math.round((state.recentActions.filter(a => a.outcome === 'success').length / state.recentActions.length) * 100)
    : 0;

  return (
    <div 
      className="min-h-screen p-8"
      style={{ backgroundColor: 'var(--gray-1)' }}
    >
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-end justify-between mb-8"
      >
        <div>
          <h1 
            className="text-2xl font-semibold mb-1"
            style={{ color: 'var(--gray-14)', letterSpacing: '-0.02em' }}
          >
            {greeting}
          </h1>
          <p style={{ color: 'var(--gray-10)' }}>
            {identity?.name || 'Limen'} is{' '}
            <span style={{ color: 'var(--accent-11)' }}>
              {state?.currentActivity || 'idle'}
            </span>
          </p>
        </div>
        {state?.lastUpdated && (
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--gray-9)' }}>
            <Clock size={12} />
            <span className="font-mono">
              {new Date(state.lastUpdated).toLocaleTimeString()}
            </span>
          </div>
        )}
      </motion.div>

      {/* Stats Row */}
      <motion.div 
        variants={stagger}
        initial="hidden"
        animate="show"
        className="grid grid-cols-4 gap-4 mb-8"
      >
        <StatCard 
          label="Actions today" 
          value={actionsToday} 
          icon={Activity}
          change={{ value: 12, positive: true }}
        />
        <StatCard 
          label="Memory files" 
          value={memoryFileCount} 
          icon={Brain}
        />
        <StatCard 
          label="Explorations" 
          value={explorationCount} 
          icon={Lightbulb}
        />
        <StatCard 
          label="Voice calls" 
          value={callCount} 
          icon={Phone}
        />
      </motion.div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - 2/3 */}
        <motion.div 
          variants={stagger}
          initial="hidden"
          animate="show"
          className="col-span-2 space-y-6"
        >
          {/* Current State Card */}
          <motion.div 
            variants={fadeUp}
            className="p-6 rounded-lg"
            style={{ 
              backgroundColor: 'var(--gray-2)', 
              border: '1px solid var(--gray-4)' 
            }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                  style={{ backgroundColor: 'var(--accent-3)' }}
                >
                  {identity?.emoji || '🚪'}
                </div>
                <div>
                  <div 
                    className="text-xs font-medium uppercase tracking-wider mb-1"
                    style={{ color: 'var(--gray-9)' }}
                  >
                    Current mood
                  </div>
                  <div 
                    className="text-lg font-medium"
                    style={{ color: 'var(--gray-14)' }}
                  >
                    {state?.mood || 'Loading...'}
                  </div>
                </div>
              </div>
              
              {state?.currentActivity && (
                <div 
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
                  style={{ 
                    backgroundColor: 'rgba(48, 164, 108, 0.1)',
                    color: 'var(--success)'
                  }}
                >
                  <Zap size={12} />
                  {state.currentActivity}
                </div>
              )}
            </div>

            <div 
              className="h-px mb-6"
              style={{ backgroundColor: 'var(--gray-4)' }}
            />

            <div className="grid grid-cols-3 gap-6">
              <MindSection 
                title="On my mind" 
                items={state?.topOfMind || []}
                icon={Brain}
                accentColor="var(--accent-11)"
              />
              <MindSection 
                title="Recent learnings" 
                items={state?.recentLearnings || []}
                icon={Lightbulb}
                accentColor="var(--warning)"
              />
              <MindSection 
                title="Pondering" 
                items={state?.questionsOnMyMind || []}
                icon={Activity}
                accentColor="var(--info)"
              />
            </div>
          </motion.div>

          {/* Success Rate */}
          <motion.div 
            variants={fadeUp}
            className="p-6 rounded-lg"
            style={{ 
              backgroundColor: 'var(--gray-2)', 
              border: '1px solid var(--gray-4)' 
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <div 
                  className="text-xs font-medium uppercase tracking-wider mb-2"
                  style={{ color: 'var(--gray-9)' }}
                >
                  Success rate
                </div>
                <div className="flex items-baseline gap-2">
                  <span 
                    className="text-4xl font-semibold"
                    style={{ 
                      color: 'var(--gray-14)',
                      fontVariantNumeric: 'tabular-nums'
                    }}
                  >
                    {successRate}%
                  </span>
                  <span style={{ color: 'var(--gray-10)' }}>
                    ({state?.recentActions?.filter(a => a.outcome === 'success').length || 0}/{state?.recentActions?.length || 0})
                  </span>
                </div>
              </div>
              <div 
                className="w-24 h-2 rounded-full overflow-hidden"
                style={{ backgroundColor: 'var(--gray-4)' }}
              >
                <div 
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${successRate}%`,
                    backgroundColor: 'var(--success)'
                  }}
                />
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Right Column - 1/3 */}
        <motion.div 
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="p-6 rounded-lg"
          style={{ 
            backgroundColor: 'var(--gray-2)', 
            border: '1px solid var(--gray-4)' 
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <span 
              className="text-xs font-medium uppercase tracking-wider"
              style={{ color: 'var(--gray-9)' }}
            >
              Recent activity
            </span>
            <span 
              className="text-xs px-2 py-0.5 rounded"
              style={{ 
                backgroundColor: 'var(--gray-4)',
                color: 'var(--gray-11)'
              }}
            >
              {state?.recentActions?.length || 0}
            </span>
          </div>
          
          <div className="space-y-0">
            {(state?.recentActions || []).slice(0, 8).map((action, i) => (
              <ActivityItem 
                key={`${action.timestamp}-${i}`}
                action={action.action}
                timestamp={action.timestamp}
                outcome={action.outcome}
              />
            ))}
            {(!state?.recentActions || state.recentActions.length === 0) && (
              <div 
                className="text-sm py-8 text-center"
                style={{ color: 'var(--gray-9)' }}
              >
                No recent activity
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
