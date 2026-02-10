import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle, Clock } from 'lucide-react';

interface Action {
  action: string;
  target?: string;
  timestamp: string;
  outcome: 'success' | 'error' | 'pending';
}

interface Props {
  actions: Action[];
}

const config = {
  success: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400' },
  error: { icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-400' },
  pending: { icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400' },
};

export const ActionTimeline: React.FC<Props> = ({ actions }) => (
  <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
    <div className="relative">
      <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gradient-to-b from-emerald-500 via-amber-500 to-rose-500 opacity-60" />
      <div className="space-y-5">
        {actions.map((action, i) => {
          const { icon: Icon, color, bg } = config[action.outcome];
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="relative pl-8"
            >
              <div className={`absolute left-2 top-2 -translate-x-1/2 h-2.5 w-2.5 rounded-full ${bg} ring-4 ring-gray-900`} />
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${color}`} />
                    <span className="text-sm font-semibold text-gray-200">{action.action}</span>
                  </div>
                  {action.target && <p className="text-xs text-gray-400 mt-0.5">{action.target}</p>}
                  <p className="text-xs text-gray-500 mt-1 font-mono">{action.timestamp}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  </div>
);