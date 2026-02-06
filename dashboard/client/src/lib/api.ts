const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:3001';

let authCredentials: string | null = null;

export function setAuth(username: string, password: string) {
  authCredentials = btoa(`${username}:${password}`);
  localStorage.setItem('dashboard_auth', authCredentials);
}

export function getAuth(): string | null {
  if (!authCredentials) {
    authCredentials = localStorage.getItem('dashboard_auth');
  }
  return authCredentials;
}

export function clearAuth() {
  authCredentials = null;
  localStorage.removeItem('dashboard_auth');
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const auth = getAuth();
  if (!auth) {
    throw new Error('Not authenticated');
  }
  
  const headers = new Headers(options.headers);
  headers.set('Authorization', `Basic ${auth}`);
  
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    clearAuth();
    throw new Error('Authentication failed');
  }
  
  return response;
}

export const api = {
  async getFile(filename: string): Promise<{ content: string; modified: string }> {
    const res = await fetchWithAuth(`/api/files/${filename}`);
    if (!res.ok) throw new Error(`Failed to fetch ${filename}`);
    return res.json();
  },
  
  async saveFile(filename: string, content: string): Promise<void> {
    const res = await fetchWithAuth(`/api/files/${filename}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) throw new Error(`Failed to save ${filename}`);
  },
  
  async getMemoryFiles(): Promise<{ files: Array<{ name: string; date: string; modified: string; preview: string; content: string }> }> {
    const res = await fetchWithAuth('/api/memory');
    if (!res.ok) throw new Error('Failed to fetch memory files');
    return res.json();
  },
  
  async getMemoryFile(date: string): Promise<{ content: string; modified: string }> {
    const res = await fetchWithAuth(`/api/memory/${date}`);
    if (!res.ok) throw new Error(`Failed to fetch memory file for ${date}`);
    return res.json();
  },
  
  async getConfig(): Promise<{ content: any; raw: string }> {
    const res = await fetchWithAuth('/api/config');
    if (!res.ok) throw new Error('Failed to fetch config');
    return res.json();
  },
  
  async getLogs(): Promise<{ lines: string[]; file: string }> {
    const res = await fetchWithAuth('/api/logs');
    if (!res.ok) throw new Error('Failed to fetch logs');
    return res.json();
  },
  
  async getGatewayStatus(): Promise<{ online: boolean; error?: string }> {
    const res = await fetchWithAuth('/api/gateway/status');
    if (!res.ok) throw new Error('Failed to fetch gateway status');
    return res.json();
  },
  
  async getCalls(): Promise<{ calls: Array<{ date: string; target: string; context: string }> }> {
    const res = await fetchWithAuth('/api/calls');
    if (!res.ok) throw new Error('Failed to fetch calls');
    return res.json();
  },
  
  async search(query: string): Promise<{ results: Array<{ file: string; matches: Array<{ line: string; num: number }> }> }> {
    const res = await fetchWithAuth(`/api/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to search');
    return res.json();
  },
  
  async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return res.ok;
    } catch {
      return false;
    }
  },
  
  async getState(): Promise<{
    lastUpdated: string | null;
    mood: string;
    topOfMind: string[];
    recentLearnings: string[];
    currentActivity: string | null;
    recentActions: Array<{ action: string; target?: string; timestamp: string; outcome: string; notes?: string }>;
    questionsOnMyMind: string[];
  }> {
    const res = await fetchWithAuth('/api/state');
    if (!res.ok) throw new Error('Failed to fetch state');
    return res.json();
  },
  
  async getDebugActions(): Promise<{
    actions: Array<{
      type: string;
      startTime: string;
      steps: Array<{ time: string; event: string; detail: string }>;
      status: string;
    }>;
  }> {
    const res = await fetchWithAuth('/api/debug/actions');
    if (!res.ok) throw new Error('Failed to fetch debug actions');
    return res.json();
  },
  
  async getExplorationStream(limit = 100): Promise<{
    entries: Array<{
      timestamp: string;
      sessionId: string;
      type: string;
      content: string;
      metadata: Record<string, unknown>;
    }>;
    activeSession: boolean;
  }> {
    const res = await fetchWithAuth(`/api/exploration/stream?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch exploration stream');
    return res.json();
  },
  
  async postExplorationUpdate(data: {
    sessionId?: string;
    type: string;
    content: string;
    metadata?: Record<string, unknown>;
  }): Promise<void> {
    const res = await fetchWithAuth('/api/exploration/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to post exploration update');
  },
};

export function createWebSocket(): WebSocket {
  const auth = getAuth();
  const wsBase = import.meta.env.PROD 
    ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
    : 'ws://localhost:3001';
  return new WebSocket(`${wsBase}/ws?auth=${auth || ''}`);
}
