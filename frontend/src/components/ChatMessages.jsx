import { useEffect, useRef } from 'react'
import { Flex, Typography, Space, Spin } from 'antd'
import { RobotOutlined, UserOutlined } from '@ant-design/icons'
import CodeReviewCard from './CodeReviewCard'

const { Text } = Typography

export default function ChatMessages({ messages, loading, emptyText, onApprove, onRevise }) {
  const chatRef = useRef(null)

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  return (
    <div ref={chatRef} style={{ maxWidth: 800, margin: '0 auto' }}>
      {messages.length === 0 && !loading && (
        <Flex justify="center" align="center" style={{ paddingTop: 100, opacity: 0.5 }}>
          <Text type="secondary">{emptyText}</Text>
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
                    onApprove={onApprove}
                    onRevise={onRevise}
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
  )
}
