"""
需求审计相关 Schemas

用于产品需求审计功能的数据模型。
"""

from typing import Optional

from pydantic import BaseModel, Field


class FeatureAssessment(BaseModel):
    """特征评估模型
    
    评估需求的某个维度是否满足开发条件。
    
    Attributes:
        is_satisfied: 该特征是否已经完全清晰明确
        extracted_data: 如果满足，提取出的结构化核心数据；如果不满足，留空
        suggested_question: 如果不满足，下一步应该怎么针对性地向用户追问
    """
    is_satisfied: bool = Field(
        ...,
        description="该特征是否已经完全清晰明确"
    )
    
    extracted_data: Optional[str] = Field(
        None,
        description="如果满足，提取出的结构化核心数据；如果不满足，留空"
    )
    
    suggested_question: Optional[str] = Field(
        None,
        description="如果不满足，下一步应该怎么针对性地向用户追问"
    )


class RequirementAuditReport(BaseModel):
    """需求审计报告模型
    
    包含四大审计维度的评估结果。
    
    Attributes:
        data_entities: 数据实体边界的检测评估
        roles_permissions: 角色与权限矩阵的检测评估
        business_workflow: 核心业务流程逻辑闭环的检测评估
        ui_components: 界面与交互组件化约束的检测评估
    """
    data_entities: FeatureAssessment = Field(
        ...,
        description="数据实体边界的检测评估"
    )
    
    roles_permissions: FeatureAssessment = Field(
        ...,
        description="角色与权限矩阵的检测评估"
    )
    
    business_workflow: FeatureAssessment = Field(
        ...,
        description="核心业务流程逻辑闭环的检测评估"
    )
    
    ui_components: FeatureAssessment = Field(
        ...,
        description="界面与交互组件化约束的检测评估"
    )
    
    @property
    def all_satisfied(self) -> bool:
        """检查是否所有维度都满足
        
        Returns:
            bool: 全部满足返回 True，否则返回 False
        """
        return all([
            self.data_entities.is_satisfied,
            self.roles_permissions.is_satisfied,
            self.business_workflow.is_satisfied,
            self.ui_components.is_satisfied,
        ])
    
    def get_unsatisfied_suggestions(self) -> list[str]:
        """获取未满足维度的改进建议
        
        Returns:
            list[str]: 改进建议列表
        """
        suggestions = []
        
        # 遍历所有维度
        for dimension_name in [
            "data_entities",
            "roles_permissions",
            "business_workflow",
            "ui_components"
        ]:
            assessment = getattr(self, dimension_name)
            
            # 如果未满足且有建议，添加到列表
            if not assessment.is_satisfied and assessment.suggested_question:
                suggestions.append(assessment.suggested_question)
        
        return suggestions
