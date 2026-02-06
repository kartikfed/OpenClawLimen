import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

export function formatTime(date: Date | string): string {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

export function formatRelative(date: Date | string): string {
  const now = new Date();
  const then = new Date(date);
  const diff = now.getTime() - then.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return formatDate(date);
}

export function parseLogLine(line: string): { type: string; content: string; timestamp?: string } {
  // Try to parse JSON log lines
  try {
    const parsed = JSON.parse(line);
    if (parsed.message) {
      const type = parsed.level === 'error' ? 'error' 
        : line.toLowerCase().includes('heartbeat') ? 'heartbeat'
        : line.toLowerCase().includes('tool') ? 'tool'
        : 'message';
      return { type, content: parsed.message, timestamp: parsed.timestamp };
    }
  } catch {}
  
  // Fallback to pattern matching
  const type = line.toLowerCase().includes('error') ? 'error'
    : line.toLowerCase().includes('heartbeat') ? 'heartbeat'
    : line.toLowerCase().includes('tool') || line.toLowerCase().includes('invoke') ? 'tool'
    : line.toLowerCase().includes('message') || line.toLowerCase().includes('telegram') ? 'message'
    : 'system';
  
  return { type, content: line };
}
