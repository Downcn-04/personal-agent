import { useReducer, useRef, useEffect, useCallback } from 'react'
import { ConfigProvider, theme, Layout, Alert } from 'antd'

import Sidebar from './components/Sidebar'
import ChatMessages from './components/ChatMessages'
import ChatInput from './components/ChatInput'
import KanbanPanel from './components/KanbanPanel'

import { fetchThreads, fetchThread, createThread, deleteThread, streamChat } from './services/api'
import sseParser from './utils/sseParser'

const { Content, Footer, Layout: AntLayout } = Layout

const initialState = {
  threads: [],
  activeThreadId: localStorage.getItem('active_thread') || '',
  messages: [],
  input: '',
  loading: false,
  error: '',
  kanbanStages: {},
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_THREADS':
      return { ...state, threads: action.payload }

    case 'SET_ACTIVE': {
      const messages = action.payload?.messages || []
      const id = action.payload?.id || ''
      return { ...state, activeThreadId: id, messages, error: '' }
    }

    case 'SET_LOADING':
      return { ...state, loading: action.payload }

    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false }

    case 'SET_INPUT':
      return { ...state, input: action.payload }

    case 'ADD_USER_MESSAGE':
      return { ...state, messages: [...state.messages, { role: 'user', content: action.payload }] }

    case 'ADD_ASSISTANT_PLACEHOLDER':
      return { ...state, messages: [...state.messages, { role: 'assistant', content: '' }] }

    case 'APPEND_CONTENT': {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last) msgs[msgs.length - 1] = { ...last, content: last.content + action.payload }
      return { ...state, messages: msgs }
    }

    case 'ADD_CODE_REVIEW':
      return {
        ...state,
        messages: [...state.messages, {
          role: 'dev',
          type: 'code_review',
          files: action.payload.files || [],
          summary: action.payload.summary || '',
        }],
      }

    case 'SET_STAGE_STATUS':
      return {
        ...state,
        kanbanStages: {
          ...state.kanbanStages,
          [action.payload.stage]: {
            ...state.kanbanStages[action.payload.stage],
            status: action.payload.status,
          },
        },
      }

    case 'SET_STAGE_DATA':
      return {
        ...state,
        kanbanStages: {
          ...state.kanbanStages,
          [action.payload.stage]: {
            ...state.kanbanStages[action.payload.stage],
            data: action.payload.data,
          },
        },
      }

    case 'RESET':
      return {
        ...state,
        activeThreadId: '',
        messages: [],
        input: '',
        loading: false,
        error: '',
        kanbanStages: {},
      }

    case 'REFRESH_THREADS':
      return { ...state, threads: action.payload }

    default:
      return state
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const abortRef = useRef(null)

  const loadThreads = useCallback(async () => {
    try {
      const data = await fetchThreads()
      dispatch({ type: 'SET_THREADS', payload: data })
    } catch {}
  }, [])

  const loadThread = useCallback(async (threadId) => {
    try {
      const data = await fetchThread(threadId)
      dispatch({ type: 'SET_ACTIVE', payload: { id: threadId, messages: data.messages || [] } })
      localStorage.setItem('active_thread', threadId)
    } catch {
      dispatch({ type: 'SET_ERROR', payload: 'Thread not found' })
    }
  }, [])

  useEffect(() => { loadThreads() }, [loadThreads])

  useEffect(() => {
    if (state.activeThreadId) loadThread(state.activeThreadId)
  }, [state.activeThreadId, loadThread])

  const handleCreate = async () => {
    try {
      const data = await createThread()
      await loadThreads()
      dispatch({ type: 'SET_ACTIVE', payload: { id: data.id, messages: [] } })
      localStorage.setItem('active_thread', data.id)
    } catch {}
  }

  const handleDelete = async (threadId) => {
    try {
      await deleteThread(threadId)
      if (state.activeThreadId === threadId) {
        localStorage.removeItem('active_thread')
        dispatch({ type: 'RESET' })
      }
      await loadThreads()
    } catch {}
  }

  const handleSend = async () => {
    const text = state.input.trim()
    if (!text || state.loading || !state.activeThreadId) return

    dispatch({ type: 'SET_INPUT', payload: '' })
    dispatch({ type: 'ADD_USER_MESSAGE', payload: text })
    dispatch({ type: 'SET_LOADING', payload: true })

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const reader = await streamChat(text, state.activeThreadId, controller.signal)
      dispatch({ type: 'ADD_ASSISTANT_PLACEHOLDER' })

      for await (const parsed of sseParser(reader)) {
        if (parsed.type === 'error') {
          dispatch({ type: 'SET_ERROR', payload: parsed.data || parsed.error })
          return
        }
        if (parsed.type === 'code_review') {
          dispatch({ type: 'ADD_CODE_REVIEW', payload: parsed })
          continue
        }
        if (parsed.type === 'stage_change') {
          dispatch({ type: 'SET_STAGE_STATUS', payload: parsed })
          continue
        }
        if (parsed.type === 'stage_data') {
          dispatch({ type: 'SET_STAGE_DATA', payload: parsed })
          continue
        }
        if (parsed.content) {
          dispatch({ type: 'APPEND_CONTENT', payload: parsed.content })
        }
      }

      await loadThreads()
    } catch (err) {
      if (err.name !== 'AbortError') {
        dispatch({ type: 'SET_ERROR', payload: err.message })
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
      abortRef.current = null
    }
  }

  const handleApprove = () => {
    dispatch({ type: 'SET_INPUT', payload: '通过，继续生成下一步代码' })
  }

  const handleRevise = () => {
    dispatch({ type: 'SET_INPUT', payload: '' })
  }

  return (
    <ConfigProvider theme={{ algorithm: theme.darkAlgorithm }}>
      <KanbanPanel stages={state.kanbanStages} />
      <AntLayout style={{ height: '100vh', flexDirection: 'row' }}>
        <Sidebar
          threads={state.threads}
          activeId={state.activeThreadId}
          onSelect={(id) => dispatch({ type: 'SET_ACTIVE', payload: { id } })}
          onCreate={handleCreate}
          onDelete={handleDelete}
        />
        <AntLayout>
          <Content style={{ flex: 1, overflowY: 'auto', padding: '8px 16px' }}>
            {state.activeThreadId ? (
              <ChatMessages
                messages={state.messages}
                loading={state.loading}
                emptyText="Send a message to start chatting"
                onApprove={handleApprove}
                onRevise={handleRevise}
              />
            ) : (
              <div ref={(el) => el} style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                paddingTop: 200,
                opacity: 0.4,
              }}>
                <span style={{ color: '#aaa' }}>Select or create a conversation to start chatting</span>
              </div>
            )}
          </Content>

          {state.error && (
            <Alert
              message={state.error}
              type="error"
              closable
              onClose={() => dispatch({ type: 'SET_ERROR', payload: '' })}
              style={{ margin: '0 16px 8px' }}
            />
          )}

          {state.activeThreadId && (
            <Footer style={{ background: 'transparent', padding: '12px 16px 16px' }}>
              <ChatInput
                value={state.input}
                onChange={(val) => dispatch({ type: 'SET_INPUT', payload: val })}
                onSend={handleSend}
                loading={state.loading}
              />
            </Footer>
          )}
        </AntLayout>
      </AntLayout>
    </ConfigProvider>
  )
}
