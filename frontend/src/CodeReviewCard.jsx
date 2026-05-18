import { Flex, Typography, Button, Space, Tag } from 'antd'
import { CheckOutlined, EditOutlined, FileOutlined, CodeOutlined } from '@ant-design/icons'

const { Text } = Typography

export default function CodeReviewCard({ files, summary, onApprove, onRevise }) {
  return (
    <div
      style={{
        maxWidth: 520,
        background: '#1a1a1a',
        border: '1px solid #303030',
        borderRadius: 12,
        padding: '14px 16px',
      }}
    >
      <Flex align="center" gap={8} style={{ marginBottom: 10 }}>
        <CodeOutlined style={{ fontSize: 16, color: '#fa8c16' }} />
        <Text strong style={{ fontSize: 13, color: '#eee' }}>Code Review</Text>
        <Tag color="processing" style={{ fontSize: 10, margin: 0 }}>待审核</Tag>
      </Flex>

      {summary && (
        <Text style={{ fontSize: 12, color: '#aaa', display: 'block', marginBottom: 8 }}>
          {summary}
        </Text>
      )}

      {files && files.length > 0 && (
        <Flex vertical gap={2} style={{ marginBottom: 12 }}>
          {files.map((f, i) => (
            <Flex
              key={i}
              align="center"
              gap={6}
              style={{
                padding: '4px 8px',
                borderRadius: 4,
                background: '#262626',
              }}
            >
              <FileOutlined style={{ fontSize: 11, color: '#888' }} />
              <Text style={{ fontSize: 11, color: '#ccc', fontFamily: 'monospace' }}>{f.path}</Text>
            </Flex>
          ))}
        </Flex>
      )}

      <Space>
        <Button
          type="primary"
          size="small"
          icon={<CheckOutlined />}
          onClick={onApprove}
          style={{ background: '#52c41a', borderColor: '#52c41a' }}
        >
          通过
        </Button>
        <Button
          size="small"
          icon={<EditOutlined />}
          onClick={onRevise}
          style={{ color: '#fa8c16', borderColor: '#fa8c16' }}
        >
          修改建议
        </Button>
      </Space>
    </div>
  )
}
