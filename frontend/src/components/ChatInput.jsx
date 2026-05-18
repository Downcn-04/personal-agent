import { Flex, Input, Button } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { useRef } from 'react'

const { TextArea } = Input

export default function ChatInput({ value, onChange, onSend, loading }) {
  const inputRef = useRef(null)

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <Flex gap={8} style={{ maxWidth: 800, margin: '0 auto' }}>
      <TextArea
        ref={inputRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
        autoSize={{ minRows: 1, maxRows: 4 }}
        style={{ flex: 1 }}
      />
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={onSend}
        disabled={loading || !value.trim()}
        style={{ alignSelf: 'flex-end' }}
      >
        Send
      </Button>
    </Flex>
  )
}
