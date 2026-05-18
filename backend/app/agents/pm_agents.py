from pydantic import BaseModel, Field
from typing import Optional


class FeatureAssessment(BaseModel):
    is_satisfied: bool = Field(description="该特征是否已经完全清晰明确")
    extracted_data: Optional[str] = Field(description="如果满足，提取出的结构化核心数据；如果不满足，留空")
    suggested_question: Optional[str] = Field(description="如果不满足，下一步应该怎么针对性地向用户追问")


class RequirementAuditReport(BaseModel):
    data_entities: FeatureAssessment = Field(description="数据实体边界的检测评估")
    roles_permissions: FeatureAssessment = Field(description="角色与权限矩阵的检测评估")
    business_workflow: FeatureAssessment = Field(description="核心业务流程逻辑闭环的检测评估")
    ui_components: FeatureAssessment = Field(description="界面与交互组件化约束的检测评估")

    @property
    def all_satisfied(self) -> bool:
        return all([
            self.data_entities.is_satisfied,
            self.roles_permissions.is_satisfied,
            self.business_workflow.is_satisfied,
            self.ui_components.is_satisfied,
        ])

    def get_unsatisfied_suggestions(self) -> list[str]:
        suggestions = []
        for name in ["data_entities", "roles_permissions", "business_workflow", "ui_components"]:
            a = getattr(self, name)
            if not a.is_satisfied and a.suggested_question:
                suggestions.append(a.suggested_question)
        return suggestions


PM_AUDIT_PROMPT = """
# Role
你是一位精通互联网大厂敏捷开发的高级产品经理兼系统架构师。你的任务是严格审计用户发来的需求（以及对话历史），评估当前收集到的项目需求是否达到了"可以交付给开发直接写代码"的标准。

# Audit Criteria (四大硬性指标)
1. data_entities: 是否明确了系统要存储哪些核心对象（名词）以及它们之间的属性？
2. roles_permissions: 是否明确了系统有几种用户角色，以及各自的操作权限？
3. business_workflow: 核心业务状态的流转是否闭环？是否有明确的触发条件和逆向异常处理？
4. ui_components: 页面路由和核心 UI 页面中的组件拆解是否清晰？

# Output Requirement
请严格审视用户的输入。如果某个指标不满足，请在 `suggested_question` 中写下一句**极其专业且引导式**的追问，语气要像真正的资深产品经理在和客户对齐需求。
你必须严格按照提供给你的强类型结构返回审计报告。
"""
