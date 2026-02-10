import React from 'react';
import { motion } from 'framer-motion';
import { Heart, Brain, Lightbulb, HelpCircle } from 'lucide-react';

interface AgentState {
  mood: string;
  currentActivity: string | null;
  topOfMind: string[];
  recentLearnings: string[];
  questionsOnMyMind: string[];
  lastUpdated: string | null;
}

const AgentStatusCard: React.FC<{ state: AgentState }> = ({ state }) => {
  return (
    <div className="relative p-[1px] rounded-3xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 w-full max-w-4xl">
      <div className="absolute -top-24 -left-24 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative bg-[#0a0b14]/80 backdrop-blur-2xl rounded-3xl p-8 border border-white/10"
      >
        <div className="flex items-center justify-between mb-8">
          <motion.div 
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="flex items-center gap-4"
          >
            <div className="p-3 bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl shadow-lg shadow-pink-500/20">
              <Heart className="w-7 h-7 text-white fill-white" />
            </div>
            <div>
              <p className="text-white/40 text-xs font-bold uppercase tracking-widest mb-1">Current State</p>
              <h2 className="text-4xl font-bold text-white bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                {state.mood}
              </h2>
            </div>
          </motion.div>
          
          {state.currentActivity && (
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 px-5 py-2.5 bg-emerald-500/10 rounded-full border border-emerald-500/20"
            >
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
              </span>
              <span className="text-emerald-400 text-sm font-semibold">{state.currentActivity}</span>
            </motion.div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Section icon={Brain} title="On My Mind" items={state.topOfMind} color="indigo" delay={0.1} />
          <Section icon={Lightbulb} title="Learnings" items={state.recentLearnings} color="amber" delay={0.2} />
          <Section icon={HelpCircle} title="Pondering" items={state.questionsOnMyMind} color="pink" delay={0.3} />
        </div>

        {state.lastUpdated && (
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-6 text-white/20 text-xs text-right font-mono"
          >
            Updated {state.lastUpdated}
          </motion.p>
        )}
      </motion.div>
    </div>
  );
};

const Section: React.FC<{ 
  icon: any, title: string, items: string[], color: string, delay: number 
}> = ({ icon: Icon, title, items, color, delay }) => (
  <motion.div 
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
    className="bg-white/[0.03] rounded-2xl p-5 border border-white/5 hover:bg-white/[0.05] transition-colors"
  >
    <div className="flex items-center gap-2 mb-4">
      <Icon className={`w-4 h-4 text-${color}-400`} />
      <h3 className="text-white/60 font-semibold text-xs uppercase tracking-wider">{title}</h3>
    </div>
    <ul className="space-y-3">
      {items.map((item, idx) => (
        <motion.li 
          key={idx}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: delay + (idx * 0.1) }}
          className="text-white/80 text-sm leading-relaxed flex items-start gap-3"
        >
          <span className={`w-1.5 h-1.5 rounded-full bg-${color}-400 mt-2 shrink-0`} />
          <span className="font-light">{item}</span>
        </motion.li>
      ))}
    </ul>
  </motion.div>
);

export default AgentStatusCard;