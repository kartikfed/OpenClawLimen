import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Users, ChevronDown } from 'lucide-react';

interface MoltbookPost {
  id: string;
  title: string;
  content: string;
  upvotes: number;
  comment_count: number;
  created_at: string;
  submolt?: { name: string };
}

interface MoltbookComment {
  id: string;
  content: string;
  post_id: string;
  post_title?: string;
  created_at: string;
}

interface MoltbookData {
  connected: boolean;
  username?: string;
  profile_url?: string;
  posts?: MoltbookPost[];
  comments?: MoltbookComment[];
  message?: string;
}

export default function MoltbookActivity() {
  const [data, setData] = useState<MoltbookData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const fetchMoltbook = useCallback(async () => {
    try {
      const response = await fetch('/api/moltbook', {
        headers: {
          'Authorization': `Basic ${btoa('kartik:openclaw2026')}`,
        },
      });
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (err) {
      console.error('Failed to fetch Moltbook data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMoltbook();
    const interval = setInterval(fetchMoltbook, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchMoltbook]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (loading) {
    return (
      <div className="bg-black/30 backdrop-blur-sm rounded-xl border border-white/5 p-4">
        <div className="flex items-center gap-2 text-white/50">
          <div className="w-3 h-3 border border-white/30 border-t-white/80 rounded-full animate-spin" />
          <span className="text-sm">Loading Moltbook...</span>
        </div>
      </div>
    );
  }

  if (!data?.connected) {
    return (
      <div className="bg-black/30 backdrop-blur-sm rounded-xl border border-white/5 p-4">
        <div className="flex items-center gap-2 text-white/40">
          <Users className="w-4 h-4" />
          <span className="text-sm">Not connected to Moltbook</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-black/30 backdrop-blur-sm rounded-xl border border-white/5 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="text-xl">🦞</div>
          <div className="text-left">
            <div className="text-sm text-white/90 font-medium">Moltbook</div>
            <div className="text-xs text-white/50">@{data.username}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {data.posts && data.posts.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400/80">
              {data.posts.length} posts
            </span>
          )}
          <ChevronDown className={`w-4 h-4 text-white/40 transition-transform ${expanded ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4 border-t border-white/5 pt-4">
              {/* Profile Link */}
              <a
                href={data.profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-xs text-cyan-400/80 hover:text-cyan-400 transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                View Profile
              </a>

              {/* Recent Posts */}
              {data.posts && data.posts.length > 0 ? (
                <div>
                  <h4 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-2">
                    My Posts
                  </h4>
                  <div className="space-y-2">
                    {data.posts.map((post) => (
                      <a
                        key={post.id}
                        href={`https://moltbook.com/p/${post.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                      >
                        <div className="text-sm text-white/80 font-medium line-clamp-1">
                          {post.title}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-white/40">
                          <span>↑ {post.upvotes}</span>
                          <span>💬 {post.comment_count}</span>
                          <span>{formatDate(post.created_at)}</span>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-xs text-white/40 italic">
                  No posts yet. Observing and learning first.
                </div>
              )}

              {/* Recent Comments */}
              {data.comments && data.comments.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-2">
                    Recent Interactions
                  </h4>
                  <div className="space-y-2">
                    {data.comments.slice(0, 3).map((comment) => (
                      <div
                        key={comment.id}
                        className="p-2 rounded-lg bg-white/5 text-xs text-white/60"
                      >
                        <div className="line-clamp-2">{comment.content}</div>
                        <div className="text-white/30 mt-1">{formatDate(comment.created_at)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
