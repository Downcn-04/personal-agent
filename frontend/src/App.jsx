import { useState, useRef, useEffect, useCallback } from 'react'
import {
  ConfigProvider,
  theme,
  Layout,
  Button,
  Input,
  Flex,
  Typography,
  Spin,
  Alert,
  Space,
} from 'antd'
import {
  SendOutlined,
  PlusOutlined,
  DeleteOutlined,
  RobotOutlined,
  UserOutlined,
  MessageOutlined,
} from '@ant-design/icons'

import KanbanPanel from './KanbanPanel'
import CodeReviewCard from './CodeReviewCard'

const { Sider, Content, Footer, Header } = Layout
const { TextArea } = Input
const { Text } = Typography

const API_URL = 'http://localhost:8000'

function App() {
  const [threads, setThreads] = useState([])
  const [activeThreadId, setActiveThreadId] = useState(() => localStorage.getItem('active_thread') || '')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [kanbanStages, setKanbanStages] = useState({})
  const chatRef = useRef(null)
  const inputRef = useRef(null)
  const abortRef = useRef(null)

  const loadThreads = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/threads`)
      const data = await res.json()
      setThreads(data)
    } catch {}
  }, [])

  const loadThread = useCallback(async (threadId) => {
    try {
      const res = await fetch(`${API_URL}/threads/${threadId}`)
      if (!res.ok) throw new Error('Not found')
      const data = await res.json()
      setMessages(data.messages || [])
      setActiveThreadId(threadId)
      localStorage.setItem('active_thread', threadId)
      setError('')
    } catch {
      setError('Thread not found')
    }
  }, [])

  useEffect(() => { loadThreads() }, [loadThreads])

  useEffect(() => {
    if (activeThreadId) {
      loadThread(activeThreadId)
    }
  }, [activeThreadId, loadThread])

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const createThread = async () => {
    try {
      const res = await fetch(`${API_URL}/threads`, { method: 'POST' })
      const data = await res.json()
      await loadThreads()
      setActiveThreadId(data.id)
    } catch {}
  }

  const deleteThread = async (threadId) => {
    try {
      await fetch(`${API_URL}/threads/${threadId}`, { method: 'DELETE' })
      if (activeThreadId === threadId) {
        setActiveThreadId('')
        setMessages([])
        localStorage.removeItem('active_thread')
      }
      await loadThreads()
    } catch {}
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading || !activeThreadId) return

    setError('')
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text, thread_id: activeThreadId }),
        signal: controller.signal,
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || `Error ${res.status}`)
      }

      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') continue

          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'error') { setError(parsed.data || parsed.error); return }
            if (parsed.type === 'code_review') {
              setMessages(prev => [...prev, {
                role: 'dev',
                type: 'code_review',
                files: parsed.files || [],
                summary: parsed.summary || '',
              }])
              continue
            }
            if (parsed.type === 'stage_change') {
              setKanbanStages(prev => ({
                ...prev,
                [parsed.stage]: { ...prev[parsed.stage], status: parsed.status },
              }))
              continue
            }
            if (parsed.type === 'stage_data') {
              setKanbanStages(prev => ({
                ...prev,
                [parsed.stage]: { ...prev[parsed.stage], data: parsed.data },
              }))
              continue
            }
            if (parsed.content) {
              setMessages(prev => {
                const msgs = [...prev]
                const last = msgs[msgs.length - 1]
                if (last) msgs[msgs.length - 1] = { ...last, content: last.content + parsed.content }
                return msgs
              })
            }
          } catch {}
        }
      }

      await loadThreads()
    } catch (err) {
      if (err.name !== 'AbortError') setError(err.message)
    } finally {
      setLoading(false)
      abortRef.current = null
    }
  }

  const handleApprove = () => {
    setInput('通过，继续生成下一步代码')
  }

  const handleRevise = () => {
    setInput('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <ConfigProvider theme={{ algorithm: theme.darkAlgorithm }}>
      <KanbanPanel stages={kanbanStages} />
      <Layout style={{ height: '100vh' }}>
        <Sider
          width={260}
          style={{
            background: '#141414',
            borderRight: '1px solid #303030',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Header style={{ background: 'transparent', padding: '12px 16px', height: 'auto' }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={createThread}
              block
            >
              New Chat
            </Button>
          </Header>
          <Flex vertical style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
            {threads.map((t) => (
              <Flex
                key={t.id}
                justify="space-between"
                align="center"
                onClick={() => setActiveThreadId(t.id)}
                style={{
                  padding: '10px 12px',
                  borderRadius: 8,
                  cursor: 'pointer',
                  background: activeThreadId === t.id ? '#1f1f1f' : 'transparent',
                  transition: 'background 0.15s',
                }}
              >
                <Space align="start" size={6} style={{ flex: 1, overflow: 'hidden' }}>
                  <MessageOutlined style={{ fontSize: 13, marginTop: 3, color: '#888' }} />
                  <Text
                    style={{ fontSize: 13, color: activeThreadId === t.id ? '#fff' : '#aaa' }}
                    ellipsis
                  >
                    {t.title || 'New Conversation'}
                  </Text>
                </Space>
                <Button
                  type="text"
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={(e) => { e.stopPropagation(); deleteThread(t.id) }}
                  style={{ color: '#666' }}
                />
              </Flex>
            ))}
            {threads.length === 0 && (
              <Flex justify="center" style={{ padding: 24, opacity: 0.4 }}>
                <Text type="secondary">No conversations yet</Text>
              </Flex>
            )}
          </Flex>
        </Sider>

        <Layout>
          <Content style={{ flex: 1, overflowY: 'auto', padding: '8px 16px' }}>
            <div ref={chatRef} style={{ maxWidth: 800, margin: '0 auto' }}>
              {!activeThreadId && (
                <Flex justify="center" align="center" style={{ paddingTop: 200, opacity: 0.4 }}>
                  <Text type="secondary">Select or create a conversation to start chatting</Text>
                </Flex>
              )}
              {activeThreadId && messages.length === 0 && !loading && (
                <Flex justify="center" align="center" style={{ paddingTop: 100, opacity: 0.5 }}>
                  <Text type="secondary">Send a message to start chatting</Text>
                </Flex>
              )}
              <Flex vertical gap={12}>
                {messages.map((msg, i) => {
                  if (msg.type === 'code_review') {
                    return (
                      <Flex key={i} justify="flex-start">
                        <Space align="start" size={8}>
                          <RobotOutlined style={{ fontSize: 18, marginTop: 8 }} />
                          <CodeReviewCard
                            files={msg.files}
                            summary={msg.summary}
                            onApprove={handleApprove}
                            onRevise={handleRevise}
                          />
                        </Space>
                      </Flex>
                    )
                  }
                  return (
                    <Flex key={i} justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}>
                      <Space align="start" size={8}>
                        {msg.role === 'assistant' && (
                          <RobotOutlined style={{ fontSize: 18, marginTop: 8 }} />
                        )}
                        <div style={{
                          maxWidth: 600,
                          padding: '10px 16px',
                          borderRadius: 12,
                          background: msg.role === 'user' ? '#1677ff' : '#262626',
                          borderBottomRightRadius: msg.role === 'user' ? 4 : 12,
                          borderBottomLeftRadius: msg.role === 'assistant' ? 4 : 12,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                        }}>
                          <Text style={{ color: '#fff' }}>{msg.content}</Text>
                        </div>
                        {msg.role === 'user' && (
                          <UserOutlined style={{ fontSize: 18, marginTop: 8 }} />
                        )}
                      </Space>
                    </Flex>
                  )
                })}
                {loading && (
                  <Flex justify="flex-start">
                    <Space align="center">
                      <Spin size="small" />
                      <Text type="secondary">Thinking...</Text>
                    </Space>
                  </Flex>
                )}
              </Flex>
            </div>
          </Content>

          {error && (
            <Alert
              message={error}
              type="error"
              closable
              onClose={() => setError('')}
              style={{ margin: '0 16px 8px' }}
            />
          )}

          {activeThreadId && (
            <Footer style={{ background: 'transparent', padding: '12px 16px 16px' }}>
              <Flex gap={8} style={{ maxWidth: 800, margin: '0 auto' }}>
                <TextArea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  style={{ flex: 1 }}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                  style={{ alignSelf: 'flex-end' }}
                >
                  Send
                </Button>
              </Flex>
            </Footer>
          )}
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}

export default App
