import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar, Clock, Phone, Brain, Sparkles, Sun, Moon, 
  RefreshCw, CheckCircle, AlertTriangle, ChevronDown,
  MessageCircle, Bell
} from 'lucide-react';
import { cn, formatRelative } from '../lib/utils';

interface CronJob {
  id: string;
  name: string;
  enabled: boolean;
  schedule: {
    kind: 'cron' | 'every' | 'at';
    expr?: string;
    tz?: string;
    at?: string;
    everyMs?: number;
  };
  sessionTarget: 'main' | 'isolated';
  payload: {
    kind: 'systemEvent' | 'agentTurn';
    message?: string;
    text?: string;
  };
  delivery?: {
    mode: 'none' | 'announce';
    channel?: string;
  };
  state?: {
    nextRunAtMs?: number;
    lastRunAtMs?: number;
    lastStatus?: 'ok' | 'error';
  };
}

const jobIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Morning Call': Phone,
  'morning-exploration': Sun,
  'evening-reflection': Moon,
  'Name Exploration': Sparkles,
  'Daily Job Application Reminder': Bell,
  'saturday-deep-dive': Brain,
  'weekly-interest-review': Calendar,
  'dynamic-greeting': MessageCircle,
};

function getJobIcon(name: string) {
  return jobIcons[name] || Clock;
}

function formatSchedule(schedule: CronJob['schedule']): string {
  if (schedule.kind === 'at' && schedule.at) {
    return new Date(schedule.at).toLocaleDateString('en-US', { 
      month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' 
    });
  }
  if (schedule.kind === 'cron' && schedule.expr) {
    // Parse common cron expressions
    const expr = schedule.expr;
    if (expr === '*/5 * * * *') return 'Every 5 min';
    if (expr === '*/15 * * * *') return 'Every 15 min';
    if (expr.match(/^0 \d+ \* \* \*$/)) {
      const hour = parseInt(expr.split(' ')[1]);
      return `Daily ${hour > 12 ? hour - 12 : hour}${hour >= 12 ? 'PM' : 'AM'}`;
    }
    if (expr.match(/^\d+ \d+ \* \* \*$/)) {
      const [min, hour] = expr.split(' ').map(n => parseInt(n));
      const h = hour > 12 ? hour - 12 : hour;
      const ampm = hour >= 12 ? 'PM' : 'AM';
      return `Daily ${h}:${min.toString().padStart(2, '0')} ${ampm}`;
    }
    if (expr.includes('* * 6')) return 'Saturdays';
    if (expr.includes('* * 0')) return 'Sundays';
    return expr;
  }
  if (schedule.kind === 'every' && schedule.everyMs) {
    const mins = Math.round(schedule.everyMs / 60000);
    if (mins < 60) return `Every ${mins} min`;
    return `Every ${Math.round(mins / 60)}h`;
  }
  return 'Custom';
}

function formatNextRun(nextRunAtMs?: number): string {
  if (!nextRunAtMs) return 'Not scheduled';
  const now = Date.now();
  const diff = nextRunAtMs - now;
  
  if (diff < 0) return 'Overdue';
  if (diff < 60000) return 'Less than 1 min';
  if (diff < 3600000) return `In ${Math.round(diff / 60000)} min`;
  if (diff < 86400000) return `In ${Math.round(diff / 3600000)} hours`;
  return new Date(nextRunAtMs).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function UpcomingTasks() {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await api.getCronJobs();
      // Sort by next run time
      const sorted = (data.jobs || []).sort((a: CronJob, b: CronJob) => {
        const aNext = a.state?.nextRunAtMs || Infinity;
        const bNext = b.state?.nextRunAtMs || Infinity;
        return aNext - bNext;
      });
      setJobs(sorted);
      setError(null);
    } catch (err) {
      console.error('Failed to load cron jobs:', err);
      setError('Failed to load scheduled tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const enabledJobs = jobs.filter(j => j.enabled);
  const nextJob = enabledJobs[0];

  return (
    <motion.div
      layout
      className="glass rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Calendar className="w-4 h-4 text-white/40" />
          <span className="text-sm font-medium text-white/80">Scheduled Tasks</span>
          <span className="text-xs text-white/30 ml-1">{enabledJobs.length} active</span>
        </div>
        <div className="flex items-center gap-3">
          {nextJob && (
            <span className="text-xs text-emerald-400/70">
              Next: {formatNextRun(nextJob.state?.nextRunAtMs)}
            </span>
          )}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => { e.stopPropagation(); loadJobs(); }}
            className="p-1 rounded-md hover:bg-white/[0.06]"
          >
            <RefreshCw className={cn('w-3 h-3 text-white/30', loading && 'animate-spin')} />
          </motion.button>
          <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-4 h-4 text-white/30" />
          </motion.div>
        </div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-white/[0.04]">
              {error ? (
                <div className="py-6 text-center">
                  <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-red-400/50" />
                  <p className="text-xs text-red-400/70">{error}</p>
                </div>
              ) : loading && jobs.length === 0 ? (
                <div className="py-6 text-center">
                  <RefreshCw className="w-6 h-6 mx-auto mb-2 text-white/20 animate-spin" />
                  <p className="text-xs text-white/30">Loading tasks...</p>
                </div>
              ) : (
                <div className="mt-3 space-y-2">
                  {enabledJobs.map((job) => {
                    const Icon = getJobIcon(job.name);
                    const isOverdue = job.state?.nextRunAtMs && job.state.nextRunAtMs < Date.now();
                    const isUpcoming = job.state?.nextRunAtMs && 
                      job.state.nextRunAtMs - Date.now() < 3600000; // Within 1 hour
                    
                    return (
                      <motion.div
                        key={job.id}
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={cn(
                          'p-3 rounded-xl border transition-colors',
                          isOverdue 
                            ? 'bg-red-500/[0.05] border-red-500/20' 
                            : isUpcoming 
                              ? 'bg-emerald-500/[0.05] border-emerald-500/20'
                              : 'bg-white/[0.02] border-white/[0.04] hover:bg-white/[0.03]'
                        )}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div className={cn(
                              'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
                              isOverdue 
                                ? 'bg-red-500/10' 
                                : isUpcoming 
                                  ? 'bg-emerald-500/10'
                                  : 'bg-white/[0.04]'
                            )}>
                              <Icon className={cn(
                                'w-4 h-4',
                                isOverdue 
                                  ? 'text-red-400/70' 
                                  : isUpcoming 
                                    ? 'text-emerald-400/70'
                                    : 'text-white/40'
                              )} />
                            </div>
                            <div className="min-w-0">
                              <h4 className="text-xs font-medium text-white/80 truncate">
                                {job.name}
                              </h4>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-[10px] text-white/30">
                                  {formatSchedule(job.schedule)}
                                </span>
                                {job.sessionTarget === 'isolated' && (
                                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400/60 border border-purple-500/10">
                                    isolated
                                  </span>
                                )}
                                {job.delivery?.mode === 'announce' && (
                                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400/60 border border-blue-500/10">
                                    announces
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <span className={cn(
                              'text-[11px] font-medium',
                              isOverdue 
                                ? 'text-red-400' 
                                : isUpcoming 
                                  ? 'text-emerald-400'
                                  : 'text-white/50'
                            )}>
                              {formatNextRun(job.state?.nextRunAtMs)}
                            </span>
                            {job.state?.lastStatus && (
                              <div className="flex items-center justify-end gap-1 mt-1">
                                {job.state.lastStatus === 'ok' ? (
                                  <CheckCircle className="w-3 h-3 text-emerald-400/50" />
                                ) : (
                                  <AlertTriangle className="w-3 h-3 text-red-400/50" />
                                )}
                                <span className="text-[9px] text-white/25">
                                  {job.state.lastRunAtMs && formatRelative(new Date(job.state.lastRunAtMs).toISOString())}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                  
                  {enabledJobs.length === 0 && (
                    <div className="py-6 text-center">
                      <Calendar className="w-6 h-6 mx-auto mb-2 text-white/10" />
                      <p className="text-xs text-white/30">No scheduled tasks</p>
                    </div>
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
