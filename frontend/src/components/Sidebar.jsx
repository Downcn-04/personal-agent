import { Layout, Button, Flex, Typography, Space } from 'antd'
import { PlusOutlined, DeleteOutlined, MessageOutlined } from '@ant-design/icons'

const { Sider, Header } = Layout
const { Text } = Typography

export default function Sidebar({ threads, activeId, onSelect, onCreate, onDelete }) {
  return (
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
        <Button type="primary" icon={<PlusOutlined />} onClick={onCreate} block>
          New Chat
        </Button>
      </Header>
      <Flex vertical style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
        {threads.map((t) => (
          <Flex
            key={t.id}
            justify="space-between"
            align="center"
            onClick={() => onSelect(t.id)}
            style={{
              padding: '10px 12px',
              borderRadius: 8,
              cursor: 'pointer',
              background: activeId === t.id ? '#1f1f1f' : 'transparent',
              transition: 'background 0.15s',
            }}
          >
            <Space align="start" size={6} style={{ flex: 1, overflow: 'hidden' }}>
              <MessageOutlined style={{ fontSize: 13, marginTop: 3, color: '#888' }} />
              <Text style={{ fontSize: 13, color: activeId === t.id ? '#fff' : '#aaa' }} ellipsis>
                {t.title || 'New Conversation'}
              </Text>
            </Space>
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              onClick={(e) => { e.stopPropagation(); onDelete(t.id) }}
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
  )
}
