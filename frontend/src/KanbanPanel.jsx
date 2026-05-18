import { useState } from 'react'
import { Flex, Typography, Tag, Button } from 'antd'
import {
  CheckCircleFilled,
  SyncOutlined,
  ClockCircleFilled,
  FileTextOutlined,
  CodeOutlined,
  BugOutlined,
  RocketOutlined,
  DoubleRightOutlined,
  DoubleLeftOutlined,
} from '@ant-design/icons'

const { Text } = Typography

const STAGES = [
  { key: 'requirements', label: '需求明确', icon: <FileTextOutlined />, color: '#1677ff' },
  { key: 'development', label: '代码开发', icon: <CodeOutlined />, color: '#fa8c16' },
  { key: 'testing', label: '测试阶段', icon: <BugOutlined />, color: '#eb2f96' },
  { key: 'deployment', label: '部署上线', icon: <RocketOutlined />, color: '#52c41a' },
]

export default function KanbanPanel({ stages }) {
  const [open, setOpen] = useState(true)

  if (!open) {
    return (
      <Button
        type="text"
        icon={<DoubleLeftOutlined />}
        onClick={() => setOpen(true)}
        style={{
          position: 'fixed',
          right: 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1000,
          width: 32,
          height: 60,
          borderTopRightRadius: 0,
          borderBottomRightRadius: 0,
          borderTopLeftRadius: 8,
          borderBottomLeftRadius: 8,
          background: '#1f1f1f',
          color: '#888',
          border: '1px solid #303030',
          borderRight: 'none',
        }}
      />
    )
  }

  return (
    <div
      style={{
        position: 'fixed',
        right: 0,
        top: '50%',
        transform: 'translateY(-50%)',
        width: 300,
        height: 300,
        zIndex: 1000,
        background: '#0d0d0d',
        border: '1px solid #303030',
        borderRadius: '10px 0 0 10px',
        padding: '12px 10px',
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        overflow: 'hidden',
      }}
    >
      <Flex justify="space-between" align="center" style={{ flexShrink: 0 }}>
        <Text strong style={{ fontSize: 12, color: '#ccc' }}>敏捷研发看板</Text>
        <Button
          type="text"
          size="small"
          icon={<DoubleRightOutlined />}
          onClick={() => setOpen(false)}
          style={{ color: '#666' }}
        />
      </Flex>

      <Flex vertical gap={4} style={{ flex: 1, overflowY: 'auto' }}>
        {STAGES.map((s) => {
          const state = stages[s.key] || { status: 'pending', data: null }
          const active = state.status === 'active'
          const done = state.status === 'completed'

          return (
            <Flex
              key={s.key}
              align="center"
              justify="space-between"
              style={{
                padding: '6px 8px',
                borderRadius: 6,
                background: active ? '#1a1a2e' : '#141414',
                border: `1px solid ${active ? s.color : '#303030'}`,
                flexShrink: 0,
              }}
            >
              <Flex align="center" gap={4} style={{ minWidth: 0 }}>
                <span style={{ fontSize: 12, color: s.color }}>{s.icon}</span>
                <Text style={{ fontSize: 11, color: active ? '#eee' : '#888' }}>{s.label}</Text>
              </Flex>
              <Flex align="center" gap={4}>
                {done ? (
                  <Tag color="success" style={{ fontSize: 10, margin: 0, lineHeight: '16px', padding: '0 4px' }}>完成</Tag>
                ) : active ? (
                  <SyncOutlined spin style={{ fontSize: 11, color: s.color }} />
                ) : (
                  <ClockCircleFilled style={{ fontSize: 10, color: '#444' }} />
                )}
              </Flex>
            </Flex>
          )
        })}
      </Flex>
    </div>
  )
}
