const API_BASE = 'http://localhost:8000';

export async function analyzeIssue(title, body) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, body }),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getHistory(limit = 5) {
  const response = await fetch(`${API_BASE}/history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }

  return response.json();
}

export async function getHistoryItem(id) {
  const response = await fetch(`${API_BASE}/history/${id}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch history item: ${response.statusText}`);
  }

  return response.json();
}
