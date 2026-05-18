const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchThreads() {
  const res = await fetch(`${API_URL}/threads`)
  return res.json()
}

export async function fetchThread(threadId) {
  const res = await fetch(`${API_URL}/threads/${threadId}`)
  if (!res.ok) throw new Error('Not found')
  return res.json()
}

export async function createThread() {
  const res = await fetch(`${API_URL}/threads`, { method: 'POST' })
  return res.json()
}

export async function deleteThread(threadId) {
  await fetch(`${API_URL}/threads/${threadId}`, { method: 'DELETE' })
}

export async function streamChat(content, threadId, signal) {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, thread_id: threadId }),
    signal,
  })

  if (!res.ok) {
    const data = await res.json()
    throw new Error(data.detail || `Error ${res.status}`)
  }

  return res.body.getReader()
}
