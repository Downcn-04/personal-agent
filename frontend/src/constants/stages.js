import {
  FileTextOutlined,
  CodeOutlined,
  BugOutlined,
  RocketOutlined,
} from '@ant-design/icons'
import { createElement } from 'react'

const STAGES = [
  { key: 'requirements', label: '需求明确', icon: createElement(FileTextOutlined), color: '#1677ff' },
  { key: 'development', label: '代码开发', icon: createElement(CodeOutlined), color: '#fa8c16' },
  { key: 'testing', label: '测试阶段', icon: createElement(BugOutlined), color: '#eb2f96' },
  { key: 'deployment', label: '部署上线', icon: createElement(RocketOutlined), color: '#52c41a' },
]

export default STAGES
