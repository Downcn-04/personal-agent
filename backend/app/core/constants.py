"""
应用常量定义模块

集中管理应用中使用的常量，避免魔法数字和硬编码字符串。
"""

# ==================== 消息相关常量 ====================

# 消息角色
class MessageRole:
    """消息角色常量"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# 消息长度限制
MAX_MESSAGE_LENGTH = 10000  # 单条消息最大长度（字符）
MAX_THREAD_TITLE_LENGTH = 50  # 会话标题最大长度（字符）


# ==================== LangGraph 相关常量 ====================

# LangGraph 节点名称
class GraphNode:
    """LangGraph 工作流节点名称"""
    PM_AUDIT = "pm_audit"  # 产品经理审计节点
    CHAT = "chat"  # 聊天节点
    DEV_READY = "dev_ready"  # 开发就绪节点


# 需要处理的聊天节点列表
CHAT_PROCESSING_NODES = [GraphNode.CHAT, GraphNode.DEV_READY]


# ==================== 事件类型常量 ====================

class EventType:
    """SSE 事件类型"""
    CONTENT = "content"  # 内容流式输出
    STAGE = "stage"  # 阶段变更
    STAGE_DATA = "stage_data"  # 阶段数据
    CODE_REVIEW = "code_review"  # 代码审查
    ERROR = "error"  # 错误
    DONE = "[DONE]"  # 完成标记


# ==================== 需求审计相关常量 ====================

class AuditDimension:
    """需求审计维度"""
    DATA_ENTITIES = "data_entities"  # 数据实体边界
    ROLES_PERMISSIONS = "roles_permissions"  # 角色与权限矩阵
    BUSINESS_WORKFLOW = "business_workflow"  # 核心业务流程逻辑闭环
    UI_COMPONENTS = "ui_components"  # 界面与交互组件化约束


# 审计维度列表（用于遍历）
AUDIT_DIMENSIONS = [
    AuditDimension.DATA_ENTITIES,
    AuditDimension.ROLES_PERMISSIONS,
    AuditDimension.BUSINESS_WORKFLOW,
    AuditDimension.UI_COMPONENTS,
]


# ==================== 研发阶段常量 ====================

class DevelopmentStage:
    """研发阶段"""
    REQUIREMENTS = "requirements"  # 需求明确
    DEVELOPMENT = "development"  # 代码开发
    TESTING = "testing"  # 测试阶段
    DEPLOYMENT = "deployment"  # 部署上线


class StageStatus:
    """阶段状态"""
    PENDING = "pending"  # 待处理
    ACTIVE = "active"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


# ==================== 数据库相关常量 ====================

# 查询限制
DEFAULT_PAGE_SIZE = 20  # 默认分页大小
MAX_PAGE_SIZE = 100  # 最大分页大小
DEFAULT_THREAD_LIST_LIMIT = 100  # 默认会话列表查询数量


# ==================== HTTP 相关常量 ====================

# API 版本
API_V1_PREFIX = "/api/v1"

# 超时设置（秒）
DEFAULT_REQUEST_TIMEOUT = 30
LLM_REQUEST_TIMEOUT = 60
