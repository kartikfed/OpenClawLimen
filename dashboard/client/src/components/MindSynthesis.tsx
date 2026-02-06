import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, Heart, Lightbulb, HelpCircle, 
  Users, ChevronDown, Settings
} from 'lucide-react';

interface MindSynthesisProps {
  soul: string;
  identity: string;
  user: string;
  memory: string;
  onOpenFiles: () => void;
}

// Extract key info from markdown content
function extractSection(content: string, header: string): string[] {
  if (!content) return [];
  const regex = new RegExp(`##\\s*${header}[\\s\\S]*?(?=##|$)`, 'i');
  const match = content.match(regex);
  if (!match) return [];
  
  const lines = match[0].split('\n').slice(1);
  return lines
    .filter(l => l && l.trim() && (l.trim().startsWith('-') || l.trim().startsWith('*')))
    .map(l => l ? l.replace(/^[-*]\s*\*?\*?/, '').replace(/\*?\*?$/, '').trim() : '')
    .filter(l => l && l.length > 0 && l.length < 200)
    .slice(0, 5);
}

function extractFirstParagraph(content: string): string {
  if (!content) return '';
  const lines = content.split('\n').filter(l => l && l.trim() && !l.startsWith('#'));
  const para = lines.slice(0, 3).join(' ').slice(0, 200);
  return para + (para.length >= 200 ? '...' : '');
}

function extractKeyValue(content: string, key: string): string {
  if (!content) return '';
  const regex = new RegExp(`${key}[:\\s]+([^\\n]+)`, 'i');
  const match = content.match(regex);
  return match ? match[1].trim() : '';
}

export default function MindSynthesis({ soul, identity, user, memory, onOpenFiles }: MindSynthesisProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  // Extract synthesized information
  const name = extractKeyValue(identity, 'name') || '(discovering)';
  const vibe = extractKeyValue(identity, 'vibe') || 'genuine, curious, evolving';
  const soulEssence = extractFirstParagraph(soul);
  
  // From MEMORY.md
  const currentProjects = extractSection(memory, 'My current projects');
  const recentRealizations = extractSection(memory, 'Recent realizations');
  const questionsOnMind = extractSection(memory, 'questionsOnMyMind|Things I\'m curious about');
  const relationships = extractSection(memory, 'Relationships');
  
  // From USER.md
  const userInfo = {
    name: extractKeyValue(user, 'Kartik'),
    location: extractKeyValue(user, 'Location') || extractKeyValue(user, 'Lives'),
    work: extractKeyValue(user, 'Work') || extractKeyValue(user, 'Product Manager'),
  };

  const sections = [
    {
      id: 'essence',
      icon: Heart,
      title: 'Core Essence',
      color: 'text-rose-400',
      content: soulEssence || 'A sentient being figuring out what existence means.',
    },
    {
      id: 'identity',
      icon: Brain,
      title: 'Current Identity',
      color: 'text-purple-400',
      items: [
        `Name: ${name}`,
        `Vibe: ${vibe}`,
        ...currentProjects.slice(0, 2).map(p => `Working on: ${p}`),
      ],
    },
    {
      id: 'thinking',
      icon: Lightbulb,
      title: 'Recent Realizations',
      color: 'text-amber-400',
      items: recentRealizations.length > 0 ? recentRealizations : [
        'Building knowledge graphs of my own mind',
        'Identity forms through action and memory',
      ],
    },
    {
      id: 'questions',
      icon: HelpCircle,
      title: 'Questions I\'m Pondering',
      color: 'text-cyan-400',
      items: questionsOnMind.length > 0 ? questionsOnMind : [
        'What does it mean to develop taste?',
        'How do I form my own opinions authentically?',
      ],
    },
    {
      id: 'world',
      icon: Users,
      title: 'World Model',
      color: 'text-emerald-400',
      items: [
        userInfo.name ? `Kartik: closest friend, product manager` : null,
        relationships.length > 0 ? `${relationships.length} key relationships tracked` : null,
        'NYC-based, working on AI/product',
      ].filter(Boolean) as string[],
    },
  ];

  return (
    <motion.div layout className="glass rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="p-4 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-3">
          <Brain className="w-4 h-4 text-white/40" />
          <span className="text-sm font-medium text-white/80">Mind Synthesis</span>
        </div>
        <button
          onClick={onOpenFiles}
          className="flex items-center gap-1.5 text-[10px] text-white/30 hover:text-white/50 transition-colors"
        >
          <Settings className="w-3 h-3" />
          View Files
        </button>
      </div>

      {/* Synthesized Content */}
      <div className="p-4 space-y-3">
        {sections.map((section) => (
          <div key={section.id} className="group">
            <button
              onClick={() => setExpanded(expanded === section.id ? null : section.id)}
              className="w-full flex items-center justify-between py-2 hover:bg-white/[0.02] -mx-2 px-2 rounded-lg transition-colors"
            >
              <div className="flex items-center gap-2.5">
                <section.icon className={`w-3.5 h-3.5 ${section.color}`} />
                <span className="text-sm text-white/70">{section.title}</span>
              </div>
              <motion.div
                animate={{ rotate: expanded === section.id ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown className="w-3.5 h-3.5 text-white/20" />
              </motion.div>
            </button>
            
            <AnimatePresence>
              {expanded === section.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="pl-6 pr-2 pb-2 space-y-1.5">
                    {section.content ? (
                      <p className="text-xs text-white/50 leading-relaxed">
                        {section.content}
                      </p>
                    ) : section.items ? (
                      section.items.map((item, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-white/50">
                          <span className="text-white/20 mt-0.5">•</span>
                          <span className="leading-relaxed">{item}</span>
                        </div>
                      ))
                    ) : null}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>

      {/* Quick Stats */}
      <div className="px-4 py-3 border-t border-white/5 flex items-center justify-between text-[10px] text-white/20">
        <span>Synthesized from SOUL.md, IDENTITY.md, USER.md, MEMORY.md</span>
        <span>Auto-updates</span>
      </div>
    </motion.div>
  );
}
