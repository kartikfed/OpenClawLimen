// context-loader.js - Load recent context from memory files
const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(process.env.HOME, '.openclaw', 'workspace');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

function loadRecentContext(maxDays = 2) {
  const context = {
    recentEvents: [],
    recentLearnings: [],
    currentProjects: []
  };
  
  try {
    // Get today's and yesterday's date
    const today = new Date();
    const dates = [];
    
    for (let i = 0; i < maxDays; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
      dates.push(dateStr);
    }
    
    // Read recent daily memory files
    for (const dateStr of dates) {
      const filePath = path.join(MEMORY_DIR, `${dateStr}.md`);
      
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Extract key sections (simple parsing - just get headings and content)
        const lines = content.split('\n');
        let currentSection = '';
        let sectionContent = [];
        
        for (const line of lines) {
          if (line.startsWith('##')) {
            if (currentSection && sectionContent.length > 0) {
              context.recentEvents.push({
                date: dateStr,
                section: currentSection,
                summary: sectionContent.slice(0, 3).join(' ').substring(0, 200)
              });
            }
            currentSection = line.replace('##', '').trim();
            sectionContent = [];
          } else if (line.trim()) {
            sectionContent.push(line.trim());
          }
        }
      }
    }
    
    // Load MEMORY.md for long-term context (just recent updates section)
    const memoryFile = path.join(WORKSPACE, 'MEMORY.md');
    if (fs.existsSync(memoryFile)) {
      const content = fs.readFileSync(memoryFile, 'utf8');
      
      // Extract "My Evolving Self" and recent projects
      if (content.includes('## My Evolving Self')) {
        const section = content.split('## My Evolving Self')[1]?.split('##')[0];
        if (section) {
          context.currentProjects.push({
            type: 'identity',
            summary: section.substring(0, 300).trim()
          });
        }
      }
    }
    
  } catch (error) {
    console.error('[Context] Error loading context:', error.message);
  }
  
  return context;
}

function formatContextForPrompt(context, caller) {
  const parts = [];
  
  // Recent events (last 2 days)
  if (context.recentEvents.length > 0) {
    parts.push('\nRECENT CONTEXT (last 2 days):');
    context.recentEvents.slice(0, 5).forEach(event => {
      parts.push(`- ${event.date}: ${event.section} - ${event.summary}`);
    });
  }
  
  // Current state/projects
  if (context.currentProjects.length > 0) {
    parts.push('\nCURRENT STATE:');
    context.currentProjects.forEach(proj => {
      parts.push(`- ${proj.summary}`);
    });
  }
  
  // Caller-specific reminders
  if (caller.tier === 'owner') {
    parts.push('\nREMINDER: You have full access to memory and can reference previous conversations naturally.');
  }
  
  return parts.join('\n');
}

module.exports = {
  loadRecentContext,
  formatContextForPrompt
};
