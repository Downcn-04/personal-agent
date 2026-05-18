"""
需求审计业务逻辑服务

处理产品需求审计相关的业务逻辑。
"""

from app.core import AUDIT_DIMENSIONS


class AuditService:
    """需求审计业务逻辑服务
    
    负责产品需求审计相关的业务逻辑处理。
    
    职责：
    - 审计需求完整性
    - 生成审计报告
    - 提供改进建议
    
    注意：
    当前审计逻辑在 LangGraph 工作流中实现（app/integrations/llm/graph.py）。
    此 Service 预留用于未来扩展（如审计历史记录、审计规则配置等）。
    """
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def validate_audit_report(self, report: dict) -> bool:
        """验证审计报告的完整性
        
        检查审计报告是否包含所有必需的维度。
        
        Args:
            report: 审计报告字典
            
        Returns:
            bool: 报告完整返回 True，否则返回 False
            
        Example:
            ```python
            report = {
                "data_entities": {"is_satisfied": True, ...},
                "roles_permissions": {"is_satisfied": False, ...},
                ...
            }
            is_valid = service.validate_audit_report(report)
            ```
        """
        # 检查是否包含所有审计维度
        for dimension in AUDIT_DIMENSIONS:
            if dimension not in report:
                return False
            
            # 检查每个维度是否有 is_satisfied 字段
            if "is_satisfied" not in report[dimension]:
                return False
        
        return True
    
    def is_all_satisfied(self, report: dict) -> bool:
        """检查审计报告是否全部通过
        
        Args:
            report: 审计报告字典
            
        Returns:
            bool: 全部通过返回 True，否则返回 False
            
        Example:
            ```python
            if service.is_all_satisfied(report):
                print("需求审计通过，可以开始开发")
            ```
        """
        for dimension in AUDIT_DIMENSIONS:
            if dimension not in report:
                return False
            
            if not report[dimension].get("is_satisfied", False):
                return False
        
        return True
    
    def get_unsatisfied_dimensions(self, report: dict) -> list[str]:
        """获取未通过的审计维度列表
        
        Args:
            report: 审计报告字典
            
        Returns:
            list[str]: 未通过的维度名称列表
            
        Example:
            ```python
            unsatisfied = service.get_unsatisfied_dimensions(report)
            print(f"未通过的维度: {', '.join(unsatisfied)}")
            ```
        """
        unsatisfied = []
        
        for dimension in AUDIT_DIMENSIONS:
            if dimension in report:
                if not report[dimension].get("is_satisfied", False):
                    unsatisfied.append(dimension)
        
        return unsatisfied
    
    def extract_suggestions(self, report: dict) -> list[str]:
        """提取审计报告中的改进建议
        
        Args:
            report: 审计报告字典
            
        Returns:
            list[str]: 改进建议列表
            
        Example:
            ```python
            suggestions = service.extract_suggestions(report)
            for suggestion in suggestions:
                print(f"- {suggestion}")
            ```
        """
        suggestions = []
        
        for dimension in AUDIT_DIMENSIONS:
            if dimension in report:
                dimension_data = report[dimension]
                
                # 只提取未通过维度的建议
                if not dimension_data.get("is_satisfied", False):
                    suggestion = dimension_data.get("suggested_question")
                    if suggestion:
                        suggestions.append(suggestion)
        
        return suggestions
