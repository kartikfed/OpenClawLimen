import { motion } from "framer-motion";
import { useId } from "react";

interface Props {
  data: number[];
  color: "purple" | "blue" | "coral";
  width?: number;
  height?: number;
}

const colors = { purple: "#8b5cf6", blue: "#3b82f6", coral: "#f43f5e" };

export default function MiniAreaChart({ data, color, width = 200, height = 60 }: Props) {
  if (!data.length) return null;
  const id = useId();
  const c = colors[color];
  const max = Math.max(...data), min = Math.min(...data);
  const pts = data.map((v, i) => [(i / (data.length - 1 || 1)) * width, height - ((v - min) / ((max - min) || 1)) * height]);
  const line = pts.map((p, i) => `${i ? "L" : "M"} ${p[0]} ${p[1]}`).join(" ");
  const area = `${line} L ${width} ${height} L 0 ${height} Z`;
  const [ex, ey] = pts[pts.length - 1];

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={c} stopOpacity="0.3" />
          <stop offset="100%" stopColor={c} stopOpacity="0" />
        </linearGradient>
      </defs>
      <motion.path d={area} fill={`url(#${id})`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }} />
      <motion.path d={line} fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1, ease: "easeOut" }} />
      <motion.circle cx={ex} cy={ey} r="3" fill={c} initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.8 }} />
    </svg>
  );
}