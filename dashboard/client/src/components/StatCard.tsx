import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: 'purple' | 'blue' | 'coral';
  trend?: { value: number; isPositive: boolean };
  delay?: number;
}

const colorConfig = {
  purple: {
    bg: 'from-purple-500/20 to-blue-500/20',
    text: 'text-purple-400',
    glow: 'group-hover:shadow-purple-500/20',
    iconBg: 'bg-gradient-to-br from-purple-500 to-blue-600',
  },
  blue: {
    bg: 'from-blue-500/20 to-cyan-500/20',
    text: 'text-blue-400',
    glow: 'group-hover:shadow-blue-500/20',
    iconBg: 'bg-gradient-to-br from-blue-500 to-cyan-600',
  },
  coral: {
    bg: 'from-orange-500/20 to-pink-500/20',
    text: 'text-orange-400',
    glow: 'group-hover:shadow-orange-500/20',
    iconBg: 'bg-gradient-to-br from-orange-500 to-pink-600',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon: Icon,
  color,
  trend,
  delay = 0,
}) => {
  const theme = colorConfig[color];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -4, scale: 1.02 }}
      className={`group relative overflow-hidden rounded-2xl bg-[#0f111a]/80 backdrop-blur-xl border border-white/[0.08] p-6 cursor-pointer transition-all duration-500 ${theme.glow} shadow-2xl`}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${theme.bg} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      
      <div className="relative z-10 flex flex-col gap-4">
        <div className="flex items-start justify-between">
          <motion.div 
            className={`p-3 rounded-xl ${theme.iconBg} shadow-lg`}
            whileHover={{ rotate: 5, scale: 1.1 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            <Icon className="w-6 h-6 text-white" strokeWidth={2} />
          </motion.div>
          
          {trend && (
            <motion.div 
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: delay + 0.2 }}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                trend.isPositive 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}
            >
              {trend.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {Math.abs(trend.value)}%
            </motion.div>
          )}
        </div>

        <div className="space-y-1">
          <motion.h3 
            className="text-5xl font-bold text-white tracking-tight"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: delay + 0.1 }}
          >
            {value}
          </motion.h3>
          <p className="text-sm font-medium text-gray-400 uppercase tracking-wider">{label}</p>
        </div>
      </div>

      <div className={`absolute -bottom-20 -right-20 w-40 h-40 bg-gradient-to-br ${theme.bg} rounded-full blur-3xl opacity-0 group-hover:opacity-50 transition-opacity duration-700`} />
    </motion.div>
  );
};