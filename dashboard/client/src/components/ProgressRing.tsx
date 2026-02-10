import { motion } from 'framer-motion';

interface ProgressRingProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: 'purple' | 'blue' | 'coral' | 'green';
  label?: string;
}

const colorConfig = {
  purple: { start: '#a855f7', end: '#ec4899' },
  blue: { start: '#3b82f6', end: '#22d3ee' },
  coral: { start: '#f97316', end: '#f43f5e' },
  green: { start: '#10b981', end: '#22d3ee' },
};

export const ProgressRing = ({
  progress,
  size = 120,
  strokeWidth = 10,
  color = 'purple',
  label,
}: ProgressRingProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  const { start, end } = colorConfig[color];
  const gradientId = `ring-gradient-${color}-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="relative inline-flex flex-col items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={start} />
            <stop offset="100%" stopColor={end} />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: [0.4, 0, 0.2, 1], delay: 0.3 }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-3xl font-bold text-white"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8, type: 'spring' }}
        >
          {Math.round(progress)}%
        </motion.span>
        {label && <span className="text-xs text-white/50 mt-1">{label}</span>}
      </div>
    </div>
  );
};

export default ProgressRing;
