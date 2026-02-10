/**
 * Sidebar — Premium Navigation
 * 
 * Design: Linear/Vercel inspired
 * - Clean, minimal
 * - Subtle active states
 * - No excessive styling
 */

import { motion } from "framer-motion";
import { 
  LayoutDashboard, Network, Activity, Compass, FileText, 
  CheckSquare, Phone, Bug, Search, Settings, Command
} from "lucide-react";

type View = 'dashboard' | 'mind' | 'activity' | 'exploration' | 'memory' | 'calls' | 'tasks' | 'bugs' | 'search' | 'settings';

interface SidebarProps {
  currentView: View;
  onViewChange: (view: View) => void;
  identity: { name: string; emoji?: string } | null;
  online: boolean;
}

const navItems: Array<{ id: View; label: string; icon: typeof LayoutDashboard }> = [
  { id: 'dashboard', label: "Overview", icon: LayoutDashboard },
  { id: 'mind', label: "Knowledge Graph", icon: Network },
  { id: 'activity', label: "Live Logs", icon: Activity },
  { id: 'exploration', label: "Exploration", icon: Compass },
  { id: 'memory', label: "Memory", icon: FileText },
  { id: 'tasks', label: "Tasks", icon: CheckSquare },
  { id: 'calls', label: "Calls", icon: Phone },
  { id: 'bugs', label: "Issues", icon: Bug },
  { id: 'search', label: "Search", icon: Search },
];

export default function Sidebar({ currentView, onViewChange, identity, online }: SidebarProps) {
  return (
    <motion.aside 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      className="fixed left-0 top-0 bottom-0 w-56 flex flex-col"
      style={{ 
        backgroundColor: 'var(--gray-2)',
        borderRight: '1px solid var(--gray-4)'
      }}
    >
      {/* Header */}
      <div 
        className="p-4 flex items-center gap-3"
        style={{ borderBottom: '1px solid var(--gray-4)' }}
      >
        <div className="relative">
          <div 
            className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
            style={{ backgroundColor: 'var(--accent-3)' }}
          >
            {identity?.emoji || '🚪'}
          </div>
          <div 
            className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full"
            style={{ 
              backgroundColor: online ? 'var(--success)' : 'var(--gray-7)',
              border: '2px solid var(--gray-2)'
            }}
          />
        </div>
        <div className="flex-1 min-w-0">
          <div 
            className="text-sm font-medium truncate"
            style={{ color: 'var(--gray-14)' }}
          >
            {identity?.name || 'Limen'}
          </div>
          <div 
            className="text-xs"
            style={{ color: 'var(--gray-9)' }}
          >
            {online ? 'Online' : 'Offline'}
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <div className="space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors"
                style={{ 
                  backgroundColor: isActive ? 'var(--gray-4)' : 'transparent',
                  color: isActive ? 'var(--gray-14)' : 'var(--gray-10)'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--gray-3)';
                    e.currentTarget.style.color = 'var(--gray-13)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = 'var(--gray-10)';
                  }
                }}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
      
      {/* Footer */}
      <div 
        className="p-2"
        style={{ borderTop: '1px solid var(--gray-4)' }}
      >
        <button
          onClick={() => onViewChange('settings')}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors"
          style={{ 
            backgroundColor: currentView === 'settings' ? 'var(--gray-4)' : 'transparent',
            color: currentView === 'settings' ? 'var(--gray-14)' : 'var(--gray-10)'
          }}
          onMouseEnter={(e) => {
            if (currentView !== 'settings') {
              e.currentTarget.style.backgroundColor = 'var(--gray-3)';
              e.currentTarget.style.color = 'var(--gray-13)';
            }
          }}
          onMouseLeave={(e) => {
            if (currentView !== 'settings') {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = 'var(--gray-10)';
            }
          }}
        >
          <Settings size={16} />
          <span>Settings</span>
        </button>
        
        <div 
          className="flex items-center gap-2 px-3 py-2 text-xs"
          style={{ color: 'var(--gray-8)' }}
        >
          <Command size={12} />
          <span>Mission Control</span>
        </div>
      </div>
    </motion.aside>
  );
}
